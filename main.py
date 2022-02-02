import win32api
import ctypes
import time
import win32gui
from PyQt5.QtWidgets import QApplication
import sys
import cv2
import numpy as np

hwnd_title = dict()

# 匹配小跳棋的模板
temp1 = cv2.imread('temp_player2.jpg', 0)
w1, h1 = temp1.shape[::-1]
# 匹配游戏结束画面的模板
temp_end = cv2.imread('temp_end.jpg', 0)
w2, h2 = temp_end.shape[::-1]

img_music = cv2.imread('music.jpg', 0)
w3, h3 = img_music.shape[::-1]


def press(x, y, button=1):
    buttonaction = 2 ** ((2 * button) - 1)
    win32api.mouse_event(buttonaction, x, y)


def release(x, y, button=1):
    buttonaction = 2 ** (2 * button)
    win32api.mouse_event(buttonaction, x, y)


def move(x, y):
    ctypes.windll.user32.SetCursorPos(x, y)


def click(x, y, button=1):
    press(x, y, button)
    release(x, y, button)


class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_ulong),
                ("y", ctypes.c_ulong)]


def get_pos():
    point = Point()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y


def get_all_hwnd(hwnd, mouse):
    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
        hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})


# 截取跳一跳小程序的当前图像
def get_screenshot(programid):
    hwnd = programid
    app = QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    img = screen.grabWindow(hwnd).toImage()
    img.save("last.png")


# 根据距离计算鼠标按下时间
def jump(distances):
    press_time = distances * 0.00318
    move(237, 813)
    press(237, 813, 1)
    time.sleep(press_time)
    release(237, 813, 1)
    print('Press Time: %.3f' % press_time)


# 利用边缘检测的结果寻找物块的上沿和下沿 进而计算物块的中心点
def get_center(img_canny, ):
    y_top = np.nonzero([max(row) for row in img_canny[200:]])[0][0] + 200
    x_top = int(np.mean(np.nonzero(img_canny[y_top])))
    H, W = img_canny.shape
    y_bottom = y_top + 20
    for row in range(y_bottom, H):
        if img_canny[row, x_top] != 0:
            y_bottom = row
            break

    x_center, y_center = x_top, (y_top + y_bottom) // 2
    return img_canny, x_center, y_center


def eliminate_music(img_test):
    img_result = cv2.matchTemplate(img_test, img_music, cv2.TM_CCOEFF_NORMED)
    threshold = 0.7
    locs = np.where(img_result >= threshold)
    for pt in zip(*locs[::-1]):
        for j in range(pt[0], pt[0] + w3 + 2):
            for k in range(pt[1], pt[1] + h3 + 2):
                img_test[k][j] = img_test[pt[0]][pt[1]]
    return img_test


# 检测小人位置,并计算下个盒子的中心位置
def detect_player():
    img_rgb = cv2.imread('last.png', 0)
    img_match = img_rgb.copy()
    res1 = cv2.matchTemplate(img_rgb, temp1, cv2.TM_CCOEFF_NORMED)
    min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res1)
    top_left = max_loc1
    bottom_right = (top_left[0] + w1, top_left[1] + h1)
    centerloc1 = (int((top_left[0] + bottom_right[0]) / 2), int((top_left[1] + bottom_right[1]) / 2) + 43)
    # loc = eliminate_music(img_rgb)
    img_rgb = eliminate_music(img_rgb)
    cv2.imwrite('eliminate.jpg', img_rgb)
    cv2.rectangle(img_match, top_left, bottom_right, (0, 0, 255), 2)
    cv2.circle(img_match, centerloc1, 2, (255, 0, 0), 2)
    # 边缘检测
    img_rgb = cv2.GaussianBlur(img_rgb, (5, 5), 0)
    canny_img = cv2.Canny(img_rgb, 1, 10)
    cv2.imwrite('canny3.jpg', canny_img)
    # 消除player的轮廓
    for k in range(max_loc1[1], max_loc1[1] + h1):
        for b in range(max_loc1[0], max_loc1[0] + w1):
            canny_img[k][b] = 0
    img_rgb, x_center, y_center = get_center(canny_img)
    cv2.imwrite('Canny image.jpg', canny_img)
    cv2.circle(img_match, (x_center, y_center), 10, 255, -1)
    cv2.imwrite('matched result.jpg', img_match)
    return centerloc1[0], centerloc1[1], x_center, y_center


# 计算跳跃距离， 单位：像素
def cal_distance(player_x1, player_y1, jump_x1, jump_y1):
    distances = ((jump_x1 - player_x1) ** 2 + (jump_y1 - player_y1) ** 2) ** 0.5
    return distances


# 检测游戏是否结束
def check_fail():
    img_end = cv2.imread('last.png', 0)
    res_end = cv2.matchTemplate(img_end, temp_end, cv2.TM_CCOEFF_NORMED)
    min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res_end)
    Threshold = 0.8
    if max_val1 >= Threshold:
        print('游戏结束')
        return False
    else:
        return True


# 获取 跳一跳 程序 id
def get_jumpid():
    win32gui.EnumWindows(get_all_hwnd, 0)
    for h, t in hwnd_title.items():
        if t == "跳一跳":
            print(h, t)
            return h


Program_id = get_jumpid()
# Main: 跳跃
for i in range(1000):
    get_screenshot(Program_id)
    if check_fail():
        player_x, player_y, jump_x, jump_y = detect_player()
        distance = cal_distance(player_x, player_y, jump_x, jump_y)
        print('Distance: %.3f' % float(distance))
        jump(distance)
        time.sleep(3.2)
    else:
        print(i, ' Jumps.')
        break
