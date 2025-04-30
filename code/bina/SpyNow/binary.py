import cv2
import numpy as np
import tensorflow as tf
print(tf.__version__)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams
from PIL import ImageFont, ImageDraw
from PIL import Image as PILImage
from functools import lru_cache
import csv
import time

# 设置中文字体支持
rcParams["font.family"] = "SimHei"
rcParams["axes.unicode_minus"] = False  # 正确显示负号


# ================= 全局配置参数 =================
class Config:
    # 图像处理参数
    CLAHE_CLIP_LIMIT = 3.0  # 对比度限制阈值(推荐2.0-4.0)
    GAUSSIAN_KERNEL = (5, 5)  # 高斯模糊核大小(奇数)
    CANNY_THRESHOLDS = (50, 150)  # Canny边缘检测双阈值
    MORPH_KERNEL_SIZE = 5  # 形态学操作核大小

    # 水槽特征参数
    MIN_AREA = 900  # 最小区域面积(像素^2)
    ASPECT_RATIO_RANGE = (0.8, 1.2)  # 宽高比允许范围
    REAL_WIDTH_CM = 30.0  # 水槽实际物理宽度(cm)

    # 调试参数
    SHOW_PROCESS = True  # 实时显示处理过程
    SAVE_DEBUG_IMAGES = True  # 保存中间处理结果

    # CNN参数
    CNN_INPUT_SIZE = (224, 224)  # CNN输入图像尺寸
    MODEL_PATH = "liquid_level_model.h5"  # CNN模型保存路径


# ================= 定标系统类 =================
class CalibrationSystem:
    def __init__(self):
        self.px2cm = None  # 像素到厘米转换系数
        self.roi = None  # 感兴趣区域坐标

    def load_calibration(self, file_path):
        """加载已有定标数据"""
        try:
            self.px2cm = np.loadtxt(file_path)
            print(f"成功加载定标参数：1像素 = {self.px2cm}厘米")
        except Exception as e:
            print(f"定标文件加载失败：{str(e)}")


# ================= 中文标注工具类 =================
class ChineseAnnotator:
    def __init__(self):
        self.font_path = self._find_font()

    def _find_font(self):
        """自动检测系统字体路径"""
        if os.name == "nt":
            win_font = "C:/Windows/Fonts/simhei.ttf"
            if os.path.exists(win_font):
                return win_font
        linux_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
        for f in linux_fonts:
            if os.path.exists(f):
                return f
        return None

    @lru_cache(maxsize=10)
    def _get_font(self, font_size):
        """带缓存的字体加载方法"""
        try:
            return ImageFont.truetype(self.font_path, font_size)
        except:
            return ImageFont.load_default()

    def draw_text(self, img, text, position, font_size=20, color=(0, 0, 255)):
        """
        在图像上绘制中文文本
        """
        pil_color = color[::-1]  # BGR转RGB
        img_pil = PILImage.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        font = self._get_font(font_size)
        img_w, img_h = img_pil.size
        x, y = position
        text_w, text_h = font.getbbox(text)[2:]
        x = min(max(x, 0), img_w - text_w - 10)
        y = min(max(y, text_h + 5), img_h - 10)
        draw.text((x, y), text, font=font, fill=pil_color)
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def resize_with_padding(image, target_size, color=(0, 0, 0)):
    """
    保持宽高比调整图像尺寸并添加填充
    """
    h, w = image.shape[:2]
    target_w, target_h = target_size
    scale = min(target_w / w, target_h / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(image, (new_w, new_h))
    pad_w = (target_w - new_w) // 2
    pad_h = (target_h - new_h) // 2
    padded = cv2.copyMakeBorder(
        resized,
        pad_h,
        target_h - new_h - pad_h,
        pad_w,
        target_w - new_w - pad_w,
        cv2.BORDER_CONSTANT,
        value=color,
    )
    return padded


# ================= CNN模型定义 =================
def create_cnn_model(input_shape=(224, 224, 3)):
    """定义CNN回归模型"""
    model = Sequential(
        [
            Conv2D(32, (3, 3), activation="relu", input_shape=input_shape),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation="relu"),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(128, activation="relu"),
            Dense(1),  # 回归输出
        ]
    )
    model.compile(optimizer="adam", loss="mse")
    return model


def preprocess_image_for_cnn(image, target_size=(224, 224)):
    """预处理图像以适应CNN输入"""
    image = cv2.resize(image, target_size)
    image = image / 255.0  # 归一化
    return image


# ================= 图像处理模块 =================
def process_image(image_path, use_cnn=False):
    # 初始化定标系统和标注工具
    calibrator = CalibrationSystem()
    annotator = ChineseAnnotator()

    # 阶段1：图像采集与预处理
    orig_image = cv2.imread(image_path)
    if orig_image is None:
        raise FileNotFoundError("图像文件加载失败，请检查路径")

    orig_height, orig_width = orig_image.shape[:2]
    target_size = (orig_width, orig_height)

    # ROI定标处理
    roi_file = "roi.txt"
    if os.path.exists(roi_file):
        roi = np.loadtxt(roi_file, delimiter=",", dtype=int)
        calibrator.roi = roi
        print("已加载ROI区域：", calibrator.roi)
    else:
        print("请手动选择水槽区域，按Enter确认")
        roi = cv2.selectROI("选择水槽区域", orig_image, showCrosshair=True)
        cv2.destroyWindow("选择水槽区域")
        calibrator.roi = roi
        np.savetxt(roi_file, roi, fmt="%d", delimiter=",")
        print("已保存ROI区域：", roi)

    # 截取并扩展ROI区域
    x, y, w, h = calibrator.roi
    padding = 10
    x_start = max(x - padding, 0)
    y_start = max(y - padding, 0)
    x_end = min(x + w + padding, orig_image.shape[1])
    y_end = min(y + h + padding, orig_image.shape[0])
    roi_image = orig_image[y_start:y_end, x_start:x_end]

    # 图像增强处理
    hsv = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    clahe = cv2.createCLAHE(clipLimit=Config.CLAHE_CLIP_LIMIT, tileGridSize=(8, 8))
    v_eq = clahe.apply(v)
    enhanced = cv2.merge([h, s, v_eq])
    enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_HSV2BGR)
    blurred = cv2.GaussianBlur(enhanced_bgr, Config.GAUSSIAN_KERNEL, 1)

    # 边缘检测与增强
    edges = cv2.Canny(blurred, *Config.CANNY_THRESHOLDS)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (Config.MORPH_KERNEL_SIZE,) * 2)
    closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # 水槽轮廓检测
    contours, _ = cv2.findContours(
        closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    candidates = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < Config.MIN_AREA:
            continue

        rect = cv2.minAreaRect(cnt)
        (cx, cy), (w_box, h_box), angle = rect
        aspect_ratio = max(w_box, h_box) / (min(w_box, h_box) + 1e-5)
        area_score = min(1.0, area / Config.MIN_AREA)
        aspect_score = 1 - abs(aspect_ratio - 1) / 0.2
        total_score = area_score * 0.6 + aspect_score * 0.4

        if (
            total_score > 0.7
            and Config.ASPECT_RATIO_RANGE[0]
            < aspect_ratio
            < Config.ASPECT_RATIO_RANGE[1]
        ):
            candidates.append((total_score, cnt))

    if not candidates:
        raise RuntimeError("水槽定位失败，请检查图像或调整参数")

    best_cnt = max(candidates, key=lambda x: x[0])[1]
    best_cnt[:, 0, 0] += x_start
    best_cnt[:, 0, 1] += y_start

    x_box, y_box, w_box, h_box = cv2.boundingRect(best_cnt)
    calibrator.px2cm = Config.REAL_WIDTH_CM / w_box
    np.savetxt(
        "calibration.txt", [calibrator.px2cm], header="像素到厘米转换系数 (cm/px)"
    )

    # 液位高度识别
    if use_cnn and os.path.exists(Config.MODEL_PATH):
        # 使用CNN预测液位高度
        model = tf.keras.models.load_model(Config.MODEL_PATH)
        cnn_roi = preprocess_image_for_cnn(roi_image, Config.CNN_INPUT_SIZE)
        cnn_roi = np.expand_dims(cnn_roi, axis=0)
        height_px = model.predict(cnn_roi)[0][0]
    else:
        # 传统边缘检测方法
        edges_roi = cv2.Canny(enhanced_bgr, *Config.CANNY_THRESHOLDS)
        height_px = np.argmax(np.sum(edges_roi, axis=1))  # 简化的液位检测

    height_cm = height_px * calibrator.px2cm

    # 可视化结果
    result = orig_image.copy()
    cv2.drawContours(result, [best_cnt], -1, (0, 255, 0), 3)
    cv2.rectangle(
        result, (x_box, y_box), (x_box + w_box, y_box + h_box), (255, 0, 0), 2
    )

    text_lines = [
        f"宽度：{w_box}px ({w_box*calibrator.px2cm:.1f}cm)",
        f"高度：{h_box}px ({h_box*calibrator.px2cm:.1f}cm)",
        f"液位高度：{height_cm:.1f}cm",
    ]

    current_y = max(y_box - 50, 30)
    for line in text_lines:
        result = annotator.draw_text(
            img=result,
            text=line,
            position=(x_box + 10, current_y),
            font_size=20,
            color=(0, 0, 255),
        )
        current_y += 30

    enhanced_padded = resize_with_padding(enhanced_bgr, target_size)
    edges_padded = resize_with_padding(edges, target_size, color=(0, 0, 0))
    closed_padded = resize_with_padding(closed_edges, target_size, color=(0, 0, 0))

    # 第一张图：原始图像 + 定标结果
    fig, axes = plt.subplots(1, 2, figsize=(18, 12))
    axes[0].imshow(cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB))
    axes[0].set_title("原始图像")
    axes[0].axis("off")

    axes[1].imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    axes[1].set_title("定标结果")
    axes[1].axis("off")

    plt.tight_layout()
    plt.savefig("combined_result_1.png", dpi=600)

    # 第二张图：增强对比 + 形态学处理 + 边缘检测
    fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))
    axes2[0].imshow(cv2.cvtColor(enhanced_padded, cv2.COLOR_BGR2RGB))
    axes2[0].set_title("对比度增强")
    axes2[0].axis("off")

    axes2[1].imshow(closed_padded, cmap="gray")
    axes2[1].set_title("形态学处理")
    axes2[1].axis("off")

    axes2[2].imshow(edges_padded, cmap="gray")
    axes2[2].set_title("边缘检测")
    axes2[2].axis("off")

    plt.tight_layout()
    plt.savefig("combined_result_2.png", dpi=600)

    plt.show()

    if Config.SAVE_DEBUG_IMAGES:
        pil_result = PILImage.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        pil_result.save("calibration.png", dpi=(600, 600))

    return {
        "px_coords": (x_box, y_box, w_box, h_box),
        "physical_size": (w_box * calibrator.px2cm, h_box * calibrator.px2cm),
        "calibration_factor": calibrator.px2cm,
        "liquid_level_cm": height_cm,
    }


# ================= 主程序 =================
if __name__ == "__main__":
    try:
        result = process_image(r"code\bina\SpyNow\machine\machine.png", use_cnn=False)
        print("\n水槽定位报告：")
        print(f"像素坐标：X={result['px_coords'][0]}, Y={result['px_coords'][1]}")
        print(
            f"物理尺寸：宽={result['physical_size'][0]:.2f}cm, 高={result['physical_size'][1]:.2f}cm"
        )
        print(f"定标系数：1像素 = {result['calibration_factor']:.4f}cm")
        print(f"液位高度：{result['liquid_level_cm']:.2f}cm")

        # 保存数据到CSV
        with open("liquid_level_data.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Timestamp", "Liquid Level (cm)"])
            writer.writerow([time.time(), result["liquid_level_cm"]])
    except Exception as e:
        print(f"程序运行出错：{str(e)}")
