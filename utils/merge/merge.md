# 化工原理恒压过滤实验自动化数据处理及可视化改进方案
**摘要：** 针对传统化工原理恒压过滤实验中人工数据记录耗时长、数据处理流程繁琐的问题，本设计方案以数字化技术为核心，构建了一套软硬件协同的智能实验平台。基于数字化图像识别技术（OpenCV），实现了滤液水槽的自动定标、液位实时监控与数据存储；通过Python开发了数字化实验数据处理系统（ChemLabX），结合恒压过滤实验需求动态筛选数据子集，利用差分法计算$\Delta\theta/\Delta q$序列，并引入Z-score异常值检测机制实时剔除离群点；进一步依托Scikit-learn机器学习框架建立线性回归模型，对过滤方程进行数字化重拟合以提升模型精度。最终，系统将处理结果与可视化图表集成至用户交互界面。该方案通过实验流程的数字化重构，显著简化了传统人工操作环节，具有 高精度、高效率、可复现的优点，为教学、科研及工业场景提供了标准化、智能化的参考解决方案。
**关键词：** 恒压过滤实验, 图像识别，自动化数据采集与处理, 数据可视化, Python软件开发
**English Title:** Optimization of Automated Data Processing and Visualization for Constant-Pressure Filtration Experiments in Chemical Engineering Principles
**Abstract:** To address the challenges of time-consuming manual data recording and cumbersome processing in traditional constant-pressure filtration experiments of chemical engineering principles, this study proposes a smart experimental platform integrating hardware and software with digitalization as its core. Leveraging digital image recognition technology (OpenCV), the system achieves automated calibration of the filtrate tank, real-time liquid level monitoring, and data storage. A digital experimental data processing system (ChemLabX), developed in Python, dynamically filters data subsets according to the requirements of constant-pressure filtration experiments. The differential method is employed to compute the $\Delta\theta/\Delta q$ sequence, while a Z-score outlier detection mechanism dynamically eliminates anomalies. Furthermore, a linear regression model based on the Scikit-learn machine learning framework is established to digitally refit the filtration equation, thereby enhancing model accuracy. The processed results and visualizations are integrated into a user interface. By digitally reconstructing the experimental workflow, this solution significantly streamlines traditional manual operations, demonstrating advantages of high precision, efficiency, and reproducibility. It provides a standardized and intelligent reference framework for educational, research, and industrial applications in chemical engineering.
**Keywords:** Constant pressure filtration experiment, Image recognition, Automated data collection and processing, Data visualization, Python software development
## 引言
化工原理恒压过滤实验是化工专业核心基础课程的重要组成部分，不仅是教育部指定的教学内容，更是学生理解化工单元操作、培养实际动手能力和理论应用能力的关键环节。通过指导学生完成实验操作并撰写实验报告，教师能够有效提升学生的专业技能，加深其对理论知识的理解与吸收。然而，传统恒压过滤实验教学面临显著挑战：数据采集耗时长（通常持续4-6小时）、数据处理流程繁琐，不仅占用了学生大量的时间和精力，也在一定程度上限制了学生的学习体验。
随着数字信息化技术的迅猛发展，自动化与智能化技术正深刻改变教育领域<sup>[1]</sup>。将先进数字化技术融入传统实验教学，对现有实验装置和流程进行优化，使学生能够利用高效工具完成实验操作，已成为当前教育数字化转型的重要方向。化工实验教学的数字化不仅能够提升效率，还能为学生提供数据驱动的学习体验，推动教学方式从标准化向个性化和智能化转变。
针对传统恒压过滤实验<sup>[2, 3]</sup>的上述问题，本研究提出了一种高度自动化的实验处理方案。通过构建软硬件协同的智能实验平台，实现了实验数据采集、处理及图表生成的全流程自动化。具体而言，本研究基于OpenCV图像识别技术和Python编程语言，开发了一款名为ChemLabX的化工实验数据采集与处理软件。该软件利用图像识别技术实时监测滤液水位，自动记录并处理实验数据，显著简化了人工操作环节，将学生在数据采集与处理上花费的时间缩短至传统方法的1/3以内，从而大幅提升了实验效率和学生参与度。
ChemLabX软件（见下页图1）的创新性不仅体现在其高效解决恒压过滤实验数据处理难题，还在于其卓越的通用性和可扩展性。该软件设计了一个模块化框架，不仅适用于恒压过滤实验，还可无缝应用于化工原理课程中的其他典型实验，如蒸馏、萃取等，目前已集成了7个实验，为实验教学的全面数字化提供了技术支持。此外，本研究提出的自动化处理方案形成了一种可复现的结构和方法论，为后续实验流程的智能化改造奠定了基础。这种数据驱动的实验教学模式，不仅优化了当前教学体验，还为相关领域的数字化应用提供了有益探索。
![Image](figures/software_gui/software_calculated.png)
**图 1: ChemLabX 软件主界面及运行后结果**
图1展示了ChemLabX软件的主界面及运行结果。
在未进行数据导入或者数据采集的情况下，界面左侧6个按键下方的第一个显示栏（原始数据预览区）、第二个显示栏（实验数据处理结果预览区）以及右侧绘图预览区均为空白。此时为软件的初始状态。
后续有两种方式供学生完成实验数据处理，下面是对两种数据处理方式的详细叙述：
一种是将记录的实验数据通过“导入数据”按钮导入，导入的数据会自动显示到原始数据预览区供使用者校对。接下来，使用者可以依次点击“处理数据”、“绘制图形”按钮，软件会自动完成原始数据的处理以及实验数据的可视化处理，并将结果输出到实验数据处理结果预览区或可视化结果预览区。
另一种是连接外用设备，同时也是本设计方案想要达到的效果，即外接图像采集设备通过USB连接到计算机，依次点击“打开串口”、“开始采集”、“停止采集”，软件会按照预设定的实验采集配置（在CONFIG文件中配置）完成图像的采集以及图像数据的识别并将结果显示到原始数据预览区。接下来，使用者可以依次点击“处理数据”、“绘制图形”按钮，完成后续操作。
ChemLabX软件采用模块化设计，主要包括应用管理模块（App.py），负责管理各类实验的屏幕界面；数据处理模块，包含实验处理器、计算器和绘图器，负责实验数据的计算和可视化；以及工具模块，提供通用功能支持。每个实验的屏幕界面基于通用的基础屏幕类（BaseScreen）构建，而数据处理则通过特定的实验处理器调用相应的计算器和绘图器实现。具体的架构信息如图2所示。
![Image](figures/app_class/app_class.png)
**图 2: ChemLabX 软件模块**
需要特别指出的是，本优化方案并未减少实验本身所需的时间，而是通过自动化技术显著减少了学生在数据采集和处理环节所需投入的时间和精力。在传统实验中，学生需要全程参与数据采集和处理，耗费大量时间。而ChemLabX软件的引入，使这些重复性、耗时的操作得以自动化完成，从而解放了学生的时间，使他们能够将精力更多地投入到实验现象的观察、理论知识的理解以及实验报告的撰写等高阶学习活动中。这种优化方式不仅提升了实验教学的效率，还增强了学生的学习体验和自主学习能力，为教学过程注入了新的活力。
## 数字化设计方案
化工原理恒压过滤实验要求学生熟悉相应的操作器械和操作方法，通过对理论知识的学习加深对恒压过滤常数<sup>[4, 5]</sup>的认识，了解恒压过滤模型的影响因素及特性，学会$\frac{d \theta}{d q} - q$一类关系的处理方法，在实际操作过程中对理论模型进行验证。
改进的数字化设计方案需要将实验中部分流程或整个流程进行一定的数学建模，仿真模拟，实现对原有实验的补充和优化，通过信息化设计，整个实验流程得到一定的简化有助于提升学生的学习效果，学习体验。
本章首先通过对实验改进前恒压过滤实验的教学目标以及实验经改进后的教学目标和教学功能进行对比，阐述两者之间的差异性；然后，对数字化设计针对的原型实验原理和内容进行详细的介绍；最后，对数字化设计内容的科学原型、原理、数学建模过程、数据库和算法进行一定的介绍。
### 教学目标分析对比
在本节内容中，将实验优化改进前后的教学目标做对比（见表1），阐述数字化设计如何在原有实验基础上提升学生的知识掌握、技能应用和数据分析能力，使其更好地理解实验内容并应对实际挑战。
**表 1: 实验优化前后教学目标对比**

| 教学目标 | 实验优化前 | 实验优化后 |
| --- | --- | --- |
| 设备认知与操作流程 | 熟练掌握设备结构、操作流程与注意事项。 | 在前者基础上，学会使用外机设备简化实验流程 |
| 过滤动力学模型构建 | 探究压差影响与速率关系、滤饼压缩性的模型。 | 在前者基础上，探索其他模型或算法。 |
| 模型求解与模型验证 | 手动画图，手动求解 | 自动化处理数据得出结果，生成实验报告 |
| 现代自动化技术应用 | 无过多涉及 | 图像识别技术，数值模拟与实验仿真。 |

#### 实验优化前拟达到的教学目标
（1）系统认知板框压滤装置的结构组成与运行机理，熟练掌握该设备的标准化操作流程及注意事项。
（2）建立恒压工况下过滤参数（包括过滤系数$K$、单位面积虚拟滤液量$q_e$及等效过滤时间$\theta_e$）的定量表征方法，深入解析各参数间的物理关联及其调控机制。
（3）探究操作压差对过滤动力学行为的影响规律，构建滤饼可压缩性指标$s$与物料本征常数$k$的耦合计算模型。
（4）学习基于差分法的工艺参数分析方法，通过实验数据建立过滤过程微分项$\frac{d\theta}{dq}$与滤液通量$q$的数学关联。
（5）定量表征滤饼洗涤阶段的传质特性$q$，实验论证终止过滤速率与洗涤速率的动力学关系。
#### 实验优化后拟达到的教学目标
（1）系统掌握板框压滤装置的运行机理与构造特征，建立设备操作参数与工艺性能的关联认知，熟练掌握该设备的标准化操作流程及注意事项。
（2）系统解析恒压过滤参数$K$、$q_e$、$\theta_e$的测定方法，通过数值模拟，仿真模拟深化参数物理内涵及其调控机制的认知。
（3）自主构建过滤压差与速率之间的量化关系模型，完善滤饼压缩指数$s$ 与物料本构常数$k$的计算模型。
（4）应用数值微分技术建立$\frac{d\theta}{dq} - q$微分方程模型，基于机器学习算法实现实验曲线的动态拟合与特征参量提取。
（5）定量分析洗涤阶段的传质特性$q$，通过可视化技术完成过滤终了速率与洗涤速率的动力学验证。
（6）了解图像识别基本原理，利用图像识别技术、Python编程语言，实现科研数据或工业大数据可视化，提升在化工单元操作中的系统整合能力与创新应用能力。
通过数字化设计，优化后的教学目标在保持实验原有教学要求的基础上，引入图像识别技术监测滤液水位，通过USB协议将数据传输到中控台上，并通过编程语言流程化处理数据集并生成分析报告。
### 传统恒压过滤实验的原型和原理
#### 传统恒压过滤实验的原型
在未经数字化设计之前，恒压过滤实验的传统流程依赖于人工操作，其步骤如图3所示。此流程图描绘了一个简化的实验过程，从实验开始到结束共包含五个主要步骤。实验始于“开始”阶段，学生需手动准备板框压滤装置并配置悬浮液。随后进入“人工观察/高度”步骤，学生通过目视方式监测滤液或滤饼的高度变化，这一过程要求高度专注以确保数据的准确性。接下来是“人工记录数据”阶段，学生手动记录时间（$\theta$）、滤液体积（$q$或$V$）以及压力差（$\Delta p$）等关键参数，这些数据是后续分析的基础。在“人工求解”步骤中，学生根据记录的数据，手动绘制$\frac{\Delta \theta}{\Delta q}$与$\bar{q}$的关系曲线，并通过直线的斜率和截距计算过滤常数$K$和等效滤液体积$q_e$，如式(3)所述。最后，流程以“结束”阶段收尾，实验结果被整理并记录为实验报告。这种传统方法虽然有助于学生理解设备操作和过滤原理，但操作繁琐且易受人为误差影响，尤其在数据记录和计算环节。
![Image](figures/exp_de_fc/exp_de_fc_ori.png)
**图 3: 恒压过滤实验原型处理流程图**
#### 传统恒压过滤实验的原理
恒压过滤过程的数学描述建立在过滤基本方程的基础理论体系之上。而恒压过滤方程作为其具体应用形式，为实验研究提供了关键数学模型支撑，后续过滤常数的测定便是从此出发的。
为了便于理解和使用本文中出现的各种符号及其物理意义，特提供以下符号说明表（见表 2）。该表列出了在恒压过滤实验理论和数据处理中直接涉及的主要符号、其说明及单位。
**表 2: 符号说明**

| 符号 | 说明 | 单位 |
| --- | --- | --- |
| $ V $ | 滤液体积 | $\mathrm{m^3}$ |
| $ A $ | 过滤面积 | $\mathrm{m^2}$ |
| $ \theta $ | 过滤时间 | $\mathrm{s}$ |
| $ \Delta p $ | 压力差 | $\mathrm{Pa}$ |
| $ \mu $ | 滤液黏度 | $\mathrm{Pa \cdot s}$ |
| $ r $ | 滤饼比阻 | $\mathrm{m^{-1}}$ |
| $ v $ | 每获得 1 m³ 滤液所形成的滤饼体积 | $\mathrm{m^3}$ |
| $ V_e $ | 等效滤液体积 | $\mathrm{m^3}$ |
| $ q $ | 单位过滤面积上的滤液体积 | $\mathrm{m}$ |
| $ q_e $ | 单位过滤面积上的等效滤液体积 | $\mathrm{m}$ |
| $ K $ | 恒压过滤常数 | $\mathrm{m^2 / s}$ |
| $ k $ | 过滤物料特性常数 | $\mathrm{m^4 / (N \cdot s)}$ |
| $ s $ | 压缩性指数 | 无 |
| $ r' $ | 比阻常数 | $\mathrm{m^{-1}}$ |
| $ \theta_e $ | 等效过滤时间 | $\mathrm{s}$ |

对恒压过滤，有
$$
(q + q_e)^2 = K (\theta + \theta_e)
$$
将式（1）进行微分可得
$$
\frac{d \theta}{d q} = \frac{2}{K} q + \frac{2}{K} q_e
$$
这是一个直线方程式，由于实验过程中不可能测量到无穷小时间段内的滤液体积的变化，只能测量有限时间段内的滤液体积。当各数据点的时间间隔不大时，$\frac{d \theta}{d q}$ 可用增量之比 $\frac{\Delta \theta}{\Delta q}$ 来代替，于普通坐标上标绘 $\frac{d \theta}{d q} - q$ 的关系曲线：
$$
\frac{\Delta \theta}{\Delta q} = \frac{2}{K} \bar{q} + \frac{2}{K} q_e
$$
在直角坐标系中，以 $\frac{\Delta \theta}{\Delta q}$ 为纵坐标，相对应的 $\bar{q}$ 为横坐标绘图，可得一直线，直线的斜率为 $\frac{2}{K}$，截距为 $\frac{2}{K} q_e$，从而求出 $K$、$q_e$。至于 $\theta_e$，可由式（4）式求出：
$$
q_e^2 = K \theta_e
$$
改变过滤压力，可得到不同操作压力下的过滤常数 $K$ 值，根据过滤常数的定义式：
$$
K = 2k \Delta p^{1-s}
$$
两边取对数得
$$
\lg K = (1-s)\lg \Delta p + \lg (2k)
$$
在不同压力过滤时，由于 $k = \frac{1}{\mu r' v} = \text{常数}$，故 $K$ 与 $\Delta p$ 的关系在对数坐标上标绘时应是一条直线，直线的斜率为 $1-s$，由此可得滤饼的压缩性指数 $s$，然后代入式（6）求物料特性常数 $k$。
### 改进的数字化设计内容的原型和原理
改进的数字化设计针对的具体内容是恒压过滤实验数据采集和处理。在改进的数字化设计过程中，利用opencv识别液位高度，并通过USB协议传输液位高度到控制台，动态获取实验数据，然后依据恒压过滤基本模型，根据数据形状进行一定的数学建模、算法设计，通过数值仿真、可视化等手段将实验结果呈现在平台上。
#### 改进的数字化设计内容的传统实验原型
改进后经数字化设计的实验流程引入了自动化和信息化技术，大幅优化了数据采集与处理效率，其步骤如图4所示。此流程图展示了一个更为复杂的实验过程，从“开始”到“结束”包含多个并行和顺序步骤，并以“ChemLabX”系统为核心处理单元。实验初始阶段为“原始数据采集”，利用图像识别技术（如OpenCV）自动监测滤液高度，取代了人工观察。随后进入“读取数据，数据清洗滤波”步骤，通过算法去除数据中的噪声和异常值。流程后续“计算$\Delta \theta / \Delta q$”，直接计算时间变化与滤液体积变化的比率；进入“拟合模型”阶段，通过数学模型（式3）拟合数据，可选择插值法或经验公式以提高精度。进一步分析得出滤饼压缩指数$s$，利用经验关系$\lg K = (1 - s) \lg \Delta p + \lg (2k)$（式6），最终数据通过USB传输至“ChemLabX”系统进行处理和可视化，生成实验结果并结束流程。
![Image](figures/exp_de_fc/exp_de_fc.png)
**图 4: 改进的数字化设计恒压过滤实验处理流程图**
改进的数字化设计的内容的核心是数据的采集和处理。通过自动化设备获得一系列滤液高度情况下所需过滤的时间，求算出在这段变化时间内液体压力的变化$\Delta p$以及时间的变化$\theta$，然后可以通过式(3)、式(4)、式(5)、式(6)求得恒压过滤常数，滤饼压缩系数以及物料特性常数。
#### 改进的数字化设计内容的原理
在数字化设计中，原始数据采集是实验能够自动化的必要条件。过滤过程中，首先通过使用外接摄像头，实时获取滤缸（透明塑料材质且带有刻度）内液位高度的变化的图片，并将监控的图片二值化；然后，采取增强对比度，形态学分析，边缘检测等算法定标水槽位置；再者，通过传统边缘检测或可选的卷积神经网络（CNN）回归模型确定水位数据，并将测得的液位数据记录于文件中；最后，将原始数据的记录文件传输至数据处理层进一步处理获取数据处理结果和可视化结果。
![Image](figures/camera/camera.png)
**图 5: 摄像头实时监测示意图**
1.**图像采集**: 使用外接摄像头实时监测滤缸内液位高度的变化情况。摄像头通过 USB 接口连接到计算机，实时捕捉滤缸内液位高度的变化。实验数据采集过程示意图如图5 所示。采集的实验装备图像如图6所示。
![Image](figures/equipment/equipment.png)
**图 6: 实验装备采集图**
2.**图像二值化**：使用图像处理库（如 OpenCV）对采集到的图像进行二值化处理。通过设置合适的阈值，将图像转换为黑白二值图像，以便后续的水槽定位、边缘检测和液位高度识别<sup>[13]</sup>。
3.**增强对比度**：对二值化后的图像进行增强对比度处理<sup>[14]</sup>，以提高水槽的可见性。可以使用直方图均衡化等方法来增强图像的对比度。
4.**形态学处理**：使用形态学处理方法（如开运算、闭运算）对二值化后的图像进行处理，以去除噪声和小的干扰物体。通过设置合适的结构元素和迭代次数，确保水槽的清晰可见。
5.**边缘检测-1**：使用边缘检测算法（如 Canny 算法）对二值化后的图像进行处理，提取水槽的边缘信息。通过设置合适的阈值，确保水槽边缘的准确识别。
步骤2-5的处理结果如图7 所示：
![Image](figures/bina/combined_result_2.png)
**图 7: 步骤2-5的处理结果**
6.**液位高度识别**：对上述处理结果中的图进行液位高度识别。传统方法通过第二次边缘检测(边缘检测-2)获取液位数据，处理后的图像如图8所示。为进一步提高准确性和鲁棒性，提出使用卷积神经网络（CNN）回归模型作为可选方法。CNN模型接收裁剪后的感兴趣区域（ROI）图像，预测液位高度（像素单位），随后通过定标系数转换为实际高度。CNN模型需在标注数据集上训练，学习图像与液位高度的映射关系。
![Image](figures/bina/combined_result_1.png)
**图 8: 边缘检测获取液位数据**
7.**数据保存**：将识别到的一系列液位高度数据（来自传统边缘检测或CNN预测）以及对应的过滤时间数据保存为csv文件，便于后续的数据处理，数据记录格式如图9所示。
![Image](figures/csv_data/csv_data.png)
**图 9: csv数据记录格式**
在上述获得实验数据的基础上，使用Python进行编程，首先对得到的原始数据进行数据清洗和异常值检测；然后，按照恒压过滤实验原型的理论依据，通过式（3）、式（4）、式（5）、式（6）进行编程式计算，完成数据处理；最后，对得到的数据处理结果进行可视化工作。
1.**数据清洗**：对原始数据进行清洗，去除无效值（如NaN），确保数据质量。
2.**异常值检测**：通过Huber回归的残差和Z-score方法检测异常值。计算每个数据点的残差，并基于Z-score阈值识别异常值。若检测到异常值，则保存未去除异常值的数据一份，同时保存去除异常值后的数据一份，为后续可视化对比准备。
3.**数据拟合**：使用Huber回归模型对处理后的数据进行鲁棒拟合，得到恒压过滤常数 $K$、虚拟滤液量 $q_e$ 和等效过滤时间 $\theta_e$。Huber回归通过结合L1和L2损失的优势，减少异常值对拟合结果的影响。
4.**数据处理**：将清洗后的数据进行处理，计算液位高度随时间变化的关系。
5.**数据可视化**：将处理后的数据和拟合结果进行可视化，帮助分析过滤过程的动态变化，并对比去除异常值前后的结果。
#### 改进的数字化设计的数学物理建模过程
在数字化设计恒压过滤实验的过程中，首先通过摄像设备实时监测物理过程，并将其抽象化。通过图像二值化、增强对比度、形态学处理和边缘检测等技术，定位水槽位置。在定位完成后，进行第二次边缘检测以测量水槽内滤液高度的尺寸，之后将这些数据保存到文件中，并通过编程好的软件进行处理和计算。
在软件内部的处理过程中，首先进行数据清洗，去除无效值。接下来，通过Huber回归模型进行鲁棒拟合，并基于残差的Z-score方法检测异常值。Huber回归通过最小化Huber损失函数，确保拟合对异常值具有鲁棒性，而残差Z-score方法进一步提升异常值检测的精度。处理后的数据用于计算关键参数，包括过滤常数（$K$）、滤饼压缩指数（$s$）和物料特性常数（$k$）。最后，通过数值仿真与可视化技术，处理后的数据结果在终端上呈现，直观展示过滤过程的动态特性。
#### 改进的数字化设计的数学物理建模过程
在数字化设计恒压过滤实验的过程中，首先需要通过摄像设备实时监测物理过程，并将其抽象化。通过图像二值化、增强对比度以及形态学处理和边缘检测等技术，定位水槽的位置。在定位完成后，进行第二次边缘检测以测量水槽内滤液高度的尺寸，之后将这些数据保存到文件中，并通过编程好的软件进行处理和计算。
在软件内部的处理过程中，首先进行数据清洗，去除无效值。接下来，通过Z-score方法检测异常值，并将处理后的数据拷贝成两份。一份数据用于正常拟合，另一份数据则用于去除异常值后的拟合。过程中，依据恒压过滤的基本原理进行数学建模，计算出过滤常数（K）、滤饼压缩指数（s）和物料特性常数（k）等关键参数。最后，通过数值仿真与可视化技术，处理后的数据结果在终端上呈现。
以下是相关描述的数学建模过程：
在恒压过滤实验中，数据采集过程的数学建模可以通过以下几个步骤来描述。首先，使用摄像设备实时监测水槽中滤液的高度变化，并通过传统图像处理或CNN模型处理图像数据。
1. 图像二值化与对比度增强
图像二值化过程将原始图像 $ I(x, y) $ 转换为黑白图像。设定一个阈值 $ T $，对图像进行二值化处理，得到二值图像 $ I_b(x, y) $：
$$
I_b(x, y) =
\begin{cases}
1, & \text{if } I(x, y) \geq T \\
0, & \text{if } I(x, y) < T
\end{cases}
$$
接下来，进行对比度增强，增强后的图像 $ I_e(x, y) $ 可以通过对比度限制自适应直方图均衡化<sup>[15, 18]</sup>（CL\\AHE）来进行，增强的公式为：
$$
I_e(x, y) = \text{CLAHE}(I(x, y), \text{clipLimit}, \text{tileGridSize})
$$
2. 形态学处理与边缘检测
在图像增强之后，使用形态学运算（如开运算和闭运算）去除噪声<sup>[19]</sup>，得到处理后的图像 $ I_p(x, y) $：
$$
I_p(x, y) = \text{Morphology}(I_e(x, y))
$$
接着，应用边缘检测算法<sup>[16, 17]</sup>（如Canny边缘检测），得到图像中的边缘信息 $ E(x, y) $：
$$
E(x, y) = \text{Canny}(I_p(x, y), T_1, T_2)
$$
其中，$ T_1 $ 和 $ T_2 $ 是边缘检测的两个阈值。
3. 水槽定位与液位高度测量
在边缘检测后，根据检测到的轮廓计算水槽的实际位置 $ (x_s, y_s) $，并测量水槽内滤液的高度 $ h $。设水槽的实际宽度为 $ W_{\text{real}} $（单位：cm），计算像素到厘米的转换系数 $ C_{\text{px2cm}} $：
$$
C_{\text{px2cm}} = \frac{W_{\text{real}}}{W_{\text{px}}}
$$
其中，$ W_{\text{px}} $ 是水槽在图像中的宽度（单位：像素）。
传统方法通过水槽的边界，测量滤液的高度 $ h_{\text{px}} $（单位：像素），并转换为实际高度 $ h_{\text{real}} $（单位：cm）：
$$
h_{\text{real}} = h_{\text{px}} \cdot C_{\text{px2cm}}
$$
为提高测量精度，提出使用卷积神经网络<sup>[20, 21]</sup>（CNN）回归模型预测液位高度。CNN模型 $ f_{\theta} $ 接收预处理后的ROI图像 $ I_{\text{ROI}} $，输出液位高度 $ h_{\text{px}} $：
$$
h_{\text{px}} = f_{\theta}(I_{\text{ROI}})
$$
其中，$ \theta $ 为模型参数。CNN模型由多层卷积层、池化层和全连接层组成，通过最小化均方误差损失函数训练：
$$
\mathcal{L} = \frac{1}{N} \sum_{i=1}^{N} (h_i - \hat{h}_i)^2
$$
其中，$ N $ 为训练样本数，$ h_i $ 为真实液位，$ \hat{h}_i $ 为预测液位。预测的像素高度 $ h_{\text{px}} $ 转换为实际高度 $ h_{\text{real}} $ 使用上述公式。
4. 数据保存与传输
上述处理步骤后，获取的滤液高度 $ h_{\text{real}} $（来自传统方法或CNN预测）和相应的时间数据 $ t $ 将保存为数据文件，并传输至计算系统进行后续处理。
在数字化设计的过程中，处理实验数据的核心部分是通过数学模型对实验数据进行拟合、异常值检测以及模型计算。具体过程如下：
1. 数据加载与预处理
在数据加载后，首先对实验数据进行预处理（其中包含液位高度和时间变化的数据）。通过删除缺失值（NaN）以及将数据转换为数值型，确保数据的质量。将加载的数据存储在一个二维数据矩阵 $ D $，其中第 $ i $ 行是时间步长 $ \theta_i $ 和对应的液位高度 $ q_i $：
$$
D = \begin{pmatrix}
\theta_1 & q_1 \\
\theta_2 & q_2 \\
\vdots & \vdots \\
\theta_n & q_n
\end{pmatrix}
$$
2. 鲁棒线性拟合
在对数据进行清洗后，进行鲁棒线性拟合。为了得到恒压过滤常数 $ K $，基于恒压过滤理论，对实验数据进行处理。通过Huber回归模型<sup>[23]</sup>对 $ \frac{\Delta \theta}{\Delta q} $ 和 $ q $ 进行拟合，得到线性关系：
$$
\frac{\Delta \theta}{\Delta q} = \text{slope} \cdot q + \text{intercept}
$$
Huber回归通过最小化Huber损失函数来估计斜率和截距，对异常值具有鲁棒性。恒压过滤常数 $ K $ 可由斜率计算得出：
$$
\hat{K} = \frac{1}{\text{slope}}
$$
3. 异常值检测与数据清洗
在初拟合后，基于鲁棒回归的残差进行异常值检测。计算每个数据点的残差 $ r_i = y_i - \hat{y}_i $，并使用Z-score方法识别异常值：
$$
Z = \frac{|r_i|}{\sigma_r}
$$
其中，$ \sigma_r $ 是残差的标准差。如果 $ Z $ 大于预设阈值，则认为该数据点是异常值。检测到异常值后，程序会将其从数据中剔除，然后使用标准线性回归重新进行拟合。
4. 数据拟合后的计算
在移除异常值并重新拟合后，程序将再次应用线性回归模型进行拟合，得到新的恒压过滤常数 $ K $、滤饼压缩指数 $ s $ 和物料特性常数 $ k $：
$$
K = \frac{1}{\text{slope}}, \quad s = \text{由实验确定}, \quad k = \text{物料常数}
$$
5. 数值仿真与可视化
最终处理结果图<sup>[5, 6]</sup>如图10、图?、图?、图?所示（部分）：
![Image](figures/fit_res/fit_res_a.png)
![Image](figures/fit_res/fit_res_b.png)
![Image](figures/fit_res/fit_res_c.png)
![Image](figures/fit_res/fit_res_d.png)
**图 10: 拟合图结果a**
所有图像的整合结果如图11所示。
![Image](figures/fit_res/fit_res.png)
**图 11: 拟合图整合图**
\pagebreak{}
6. 最终结果与输出
所有处理后的数据将输出为CSV文件，包括滤液体积、过滤时间和恒压过滤常数等参数。数据处理结果会被保存并展示在图形界面中，帮助学生理解恒压过滤过程中的各项物理量之间的关系。
#### 数字化设计的数据库及算法设计
```latex
    \caption{数据采集数学建模}
    \begin{algorithmic}[1]
        \Require 图像数据 $I(x, y)$
        \Ensure 处理后的图像数据 $I_b(x, y)$, $I_e(x, y)$, $I_p(x, y)$，边缘检测结果 $E(x, y)$，水槽位置 $(x_s, y_s)$，液体高度 $h_{\text{real}}$
        % 图像二值化和对比度增强
        \Function{Image Binarization and Contrast Enhancement}{$I(x, y)$}
            \State 设置阈值 $T$
            \State 生成二值化图像 $I_b(x, y)$：
            \[
            I_b(x, y) =
            \begin{cases}
            1, & \text{如果 } I(x, y) \geq T \\
            0, & \text{如果 } I(x, y) < T
            \end{cases}
            \]
            \State 对图像进行增强，得到 $I_e(x, y)$：
            \[
            I_e(x, y) = \text{CLAHE}(I(x, y), \text{clipLimit}, \text{tileGridSize})
            \]
        \EndFunction
        % 图像形态学处理和边缘检测
        \Function{Morphological Processing and Edge Detection}{$I_e(x, y)$}
            \State 进行形态学操作，得到处理后的图像 $I_p(x, y)$：
            \[
            I_p(x, y) = \text{Morphology}(I_e(x, y))
            \]
            \State 应用 Canny 边缘检测，得到边缘检测结果 $E(x, y)$：
            \[
            E(x, y) = \text{Canny}(I_p(x, y), T_1, T_2)
            \]
        \EndFunction
        % 水槽位置和液体高度测量
        \Function{Tank Position and Liquid Height Measurement}{$E(x, y)$}
            \State 计算水槽位置 $(x_s, y_s)$
            \State 设置实际水槽宽度 $W_{\text{real}}$
            \State 计算像素到厘米的转换系数 $C_{\text{px2cm}}$：
            \[
            C_{\text{px2cm}} = \frac{W_{\text{real}}}{W_{\text{px}}}
            \]
            \State 测量液体高度 $h_{\text{px}}$（单位：像素），并转换为实际高度 $h_{\text{real}}$：
            \[
            h_{\text{real}} = h_{\text{px}} \cdot C_{\text{px2cm}}
            \]
        \EndFunction
        \Function{Data Saving and Transmission}{$h_{\text{real}}, t$}
            \State 保存数据并传输到计算系统进行进一步处理
        \EndFunction
    \end{algorithmic}
```
改进的恒压过滤实验图像数据采集及数据处理算法流程图见图12，其核心目的是处理从实验中获取的图像数据，并通过一系列图像处理技术提取液体容器的液位信息。
![Image](figures/algo/algo1.png)
**图 12: 数据采集算法流程图**
从图12中可看出，算法首先通过加载实验图像并选择感兴趣区域（ROI）开始处理。接着，通过CLAHE增强对比度、高斯模糊平滑图像、Canny边缘检测提取特征，并应用形态学闭运算去除噪声。随后，算法寻找并选择最佳轮廓以定位水槽，计算像素到厘米的定标系数。液位高度检测支持两种方法：传统方法通过第二次Canny边缘检测和行和最大值计算高度；可选的卷积神经网络（CNN）回归模型通过预训练模型预测高度，提高鲁棒性。最终，高度转换为实际单位，可视化并保存为CSV文件，传输至后续处理模块。
```latex
    \caption{软件内部数据处理数学建模}
    \begin{algorithmic}[1]
        \Require 实验数据矩阵 $D$
        \Ensure 过滤后的数据和模型参数 $K$, $s$, $k$
        \Function{Data Loading and Preprocessing}{$D$}
            \State 加载CSV数据，清洗数据，去除缺失值
            \State 将数据存储在二维矩阵 $D$ 中，其中第 $i$ 行表示时间步 $\theta_i$ 和液体高度 $q_i$：
            \[
            D = \begin{pmatrix}
            \theta_1 & q_1 \\
            \theta_2 & q_2 \\
            \vdots & \vdots \\
            \theta_n & q_n
            \end{pmatrix}
            \]
        \EndFunction
        \Function{Robust Linear Fitting}{$D$}
            \State 计算液体体积 $V$ 与时间之间的关系
            \State 基于恒压过滤方程，执行以下计算：
            \[
            \frac{\Delta \theta}{\Delta q} = \frac{K A^2}{2(V + V_e)}
            \]
            \State 使用Huber回归模型对数据进行拟合，求解恒压过滤常数 $K$：
            \[
            \frac{\Delta \theta}{\Delta q} = \text{slope} \cdot q + \text{intercept}
            \]
            \State 通过Huber损失函数估计斜率和截距，得到初步 $K$：
            \[
            \hat{K} = \frac{1}{\text{slope}}
            \]
        \EndFunction
        \Function{Outlier Detection and Data Cleaning}{$D$}
            \State 计算残差 $r_i = y_i - \hat{y}_i$，并使用Z分数方法：
            \[
            Z = \frac{|r_i|}{\sigma_r}
            \]
            \State 若 $Z$ 大于阈值（默认2），则移除该数据点
        \EndFunction
        \Function{Post-Fitting Calculations}{$D$}
            \State 移除异常值后，使用标准线性回归拟合，得到最终 $K$、$s$、$k$：
            \[
            K = \frac{1}{\text{slope}}, \quad s = \text{由实验确定}, \quad k = \text{物料常数}
            \]
        \EndFunction
        \Function{Numerical Simulation and Visualization}{$D$}
            \State 使用数学模型进行数值仿真，预测液体体积和高度
            \State 可视化拟合结果与实验数据，比较异常值影响
        \EndFunction
        \Function{Final Results and Output}{$K, s, k$}
            \State 输出液体体积、过滤时间和过滤常数
        \EndFunction
    \end{algorithmic}
```
改进的过滤实验数据处理算法流程图见图13，该算法通过数学建模提取液位数据，拟合出恒压过滤常数 $K$、滤饼压缩指数 $s$ 和物料特性常数 $k$。
![Image](figures/algo/algo2.png)
**图 13: 数据处理算法流程图**
从图13中可看出，算法首先加载实验数据并进行预处理，去除缺失值。接着，初始化组索引，逐组处理数据。每组数据通过提取、变量计算、Huber回归鲁棒拟合、基于残差的Z分数异常值检测、线性回归二次拟合等步骤，计算过滤常数 $K$。异常值检测确保拟合精度，二次拟合生成最终参数。所有组处理完成后，输出结果并保存为CSV文件，完成过滤过程分析。
## 实验部分
过滤是一种液-固分离的过程，通常通过施加恒定的压力，液体穿过过滤介质，固体颗粒被截留在介质表面形成滤饼。随着过滤的进行，滤饼厚度逐渐增加，液体流经的孔道长度增大，导致流动阻力增加。因此，即使维持恒定的过滤压力，过滤速率也会逐渐下降，为了获得相同的滤液量，所需的过滤时间将逐渐增加。
### 实验原理
在恒压过滤中，过滤速率的变化通常使用以下关系式描述：
$$
(q + q_{e})^2 = K (\theta + \theta_{e})
$$
其中，$q$是单位过滤面积上获得的滤液体积（$\mathrm{m}^3/\mathrm{m}^2$），$q_{e}$是单位过滤面积上的虚拟滤液体积，$\theta$为实际过滤时间，$\theta_{e}$为虚拟过滤时间，$K$为过滤常数（$\mathrm{m}^2/\mathrm{s}$）。
通过对式子微分，得
$$
\frac{d\theta}{dq} = \frac{2}{K} q + \frac{2}{K} q_{e}
$$
在实验过程中，我们通过测量有限时间段内滤液体积的变化，绘制$\frac{\Delta \theta}{\Delta q}$与$\bar{q}$的关系曲线，从而求得过滤常数$K$和虚拟滤液体积$q_{e}$。根据以下关系式：
$$
q_{e}^2 = K\theta_{e}
$$
进一步计算出虚拟过滤时间$\theta_{e}$。
**压力与过滤常数的关系**:
通过改变过滤压力$\Delta p$，可以得到不同压力下的过滤常数$K$。根据过滤常数的定义，公式如下：
$$
K = 2k\Delta p^{1-s}
$$
取对数后，得到
$$
\lg K = (1 - s)\lg \Delta p + \lg(2k)
$$
在对数坐标中，$K$与$\Delta p$的关系应该是直线，直线的斜率为$1-s$。通过这种方法可以求得滤饼的压缩性指数$s$以及物料特性常数$k$。
### 试剂与材料
**主要试剂及信息**：
轻质碳酸钙悬浮液，浓度在 $6%$ $\sim$ $8%$ 左右。
**溶液配制与保存**：
轻质碳酸钙悬浮液应在实验前配制，确保浓度控制在 $6%$ $\sim$ $8%$ 范围内。使用搅拌器保持料液均匀，防止出现旋涡。
### 仪器和表征方法
实验装置流程如图14所示。原料槽内配有一定浓度的轻质碳酸钙悬浮液（浓度在 $6%$ $\sim$ $8%$ 左右），用电动搅拌器进行均匀搅拌（以浆液不出现旋涡为好）。启动旋涡泵 19，调节阀门7使压力表11指示在规定值。滤液在计量槽内计量。
![Image](figures/equipment/equipment_1.png)
**图 14: 恒压过滤实验装置流程示意图**
1—搅拌电机；2—原料罐；3—搅拌挡板；4，14，15—排液阀；5—洗水槽；6，7—调节阀；8—温度计；9，10，12—阀门；11—压力表；13—滤液计量槽；16—板框压滤机；17—过滤机压紧装置；18—过滤板；19—旋涡泵实验装置中过滤、洗涤管路分布如图15所示。
![Image](figures/equipment/equipment_2.png)
**图 15: 板框压滤机过滤洗涤管路分布图**
（2）实验设备中主要的技术参数如表3所示
**表 3: 恒压过滤常数测定实验设备主要技术参数**

| 序号 | 名称 | 规格 | 材料 |
| --- | --- | --- | --- |
| 1 | 搅拌器 | 型号：KDZ－1 |  |
| 2 | 过滤板 | $160 \, \mathrm{mm} \times 180 \, \mathrm{mm} \times 11 \, \mathrm{mm}$ | 不锈钢 |
| 3 | 滤布 | 工业用 |  |
| 4 | 过滤面积 | $0.0475 \, \mathrm{m}^2$ |  |
| 5 | 计量桶 | 长 327 mm，宽 286 mm |  |

（3）实验装置面板图如下
![Image](figures/equipment/equipment_3.png)
**图 16: 实验装置面板图**
### 实验步骤/方法/现象
#### 实验准备工作
（1）原料罐内配好浓度在 $6% \sim 8%$ 左右的轻质碳酸钙悬浮液，系统接上电源，开启总电源，开启搅拌，使料浆搅拌均匀。
（2）在滤液水槽中加入一定高度液位的水（水位在标尺 50 mm 处即可）。
（3）板框过滤机板，框排列顺序为固定头 $\rightarrow$ 非洗涤板 $(\cdot)
\rightarrow$ 框 $(:) \rightarrow$ 洗涤板 $(⋮)\rightarrow$ 框 $(:) \rightarrow$ 非洗涤板$(\cdot)$$\rightarrow$ 可动头。用压紧装置压紧后待用。
#### 过滤实验
（1）阀门9，7全开，其他阀门全部关闭（图14）。启动旋涡泵19，打开阀门12，利用料液回水阀7调节压力，使压力表11达到规定值。
（2）待压力表11数值稳定后，打开过滤机滤液入口阀A，随后快速打开过滤机出口阀门B，C开始过滤。当计量桶13内见到第一滴液体时开始计时，记录滤液每增加高度 10 mm 时所用的时间。当计量桶 13 读数为 150 mm 时停止计时，并立即关闭过滤机进料阀 B。
（3）打开料液回水阀 7 使压力表11指示值下降，关闭泵开关。放出计量槽内的滤液倒回槽内，以保证料浆浓度保持不变。
#### 洗涤实验
（1）洗涤实验时全开阀门10，6，其他阀门全关。调节阀门6使压力表11达到过滤要求的数值。打开阀门B，随后快速打开过滤机出口阀门C开始洗涤。等到阀门B有液体流下时开始计时，洗涤量为过滤量的 $1 / 4$ 。实验结束后，放出计量槽内的滤液到洗水槽 5 内。
（2）开启压紧装置，卸下过滤框内的滤饼并放回滤浆槽内，将滤布清洗干净。
（3）改变压力值，从开始重复上述实验。压力分别为 $0.05 MPa,0.10 MPa, 0.15 MPa$ 。
#### 操作注意事项
（1）过滤板与过滤框之间的密封垫注意要放正，过滤板与过滤框上面的滤液进出口要对齐。滤板与滤框安装完毕后要用摇柄把过滤设备压紧，以免漏液。
（2）计量槽的流液管口应紧贴桶壁，防止液面波动影响读数。
（3）由于电动搅拌器为无级调速，使用时首先接上系统电源，打开调速器开关，调速钮一定由小到大缓慢调节，切勿反方向调节或调节过快，以免损坏电机。
（4）启动搅拌前，用手旋转一下搅拌轴以保证启动顺利。
（5）每次实验结束后将滤饼和滤液全部倒回料浆槽中，保证料液浓度保持不变。
过程中记录实验数据于下表4中：
**表 4: 板框压滤机过滤常数的测定**
[Table]
实验数据处理后的结果记录表5中：
**表 5: 恒压过滤常数测定实验数据处理结果**
[Table]
## 结语
本数字化设计通过自动化技术和先进数据处理方法，显著优化了恒压过滤实验的教学流程。系统利用图像识别技术实时监测滤液液位，并结合机器学习算法分析数据，不仅减少了人工操作时间，还提升了实验效率与结果准确性。该设计在教学中提供了数据驱动的学习体验，帮助学生掌握现代化工领域的核心数字化技能，具有一定的教育意义。其创新性体现在图像识别、机器学习与集成平台的结合（目前已包含7个实验），简化操作并提高精度。未来，该系统可扩展至更多实验场景，推动化学工程教育的数字化转型。
## 创新性声明
1. 数据采集方面：利用OpenCV图像识别技术，自动监测滤液液位，减少人工误差。
2. 数据处理方面：采用Scikit-learn进行机器学习建模，提升分析精度。
3. 软件设计方面：集成数据采集、处理和可视化，简化实验操作。
\pagebreak{}
{\liuhao
## 参考文献
[1] 迟松江, 路战红, 张秀红. 自动化过滤常数测定装置及应用[J]. 沈阳工业大学学报, 2001, 28(03): 255-257.	(中文期刊).
[2] 张春芝, 贾金霖, 潘志强, 等. 板框式过滤机过滤常数测定研究[J]. 北京工商大学学报(自然科学版), 2010, 28(03): 68-71.	(中文期刊).
[3] 赵帅, 郑婷婷, 李傲雪, 等. 恒压过滤常数测定实验的影响因素探究[J]. 长春师范大学学报, 2022, 41(08): 99-106.	(中文期刊).
[4] 葛艳蕊, 顾丽敏, 曹亚鹏. 恒压过滤实验中测定值偏离理论值的原因探讨[J]. 实验室科学, 2024, 27(01): 54-57.	(中文期刊).
[5] 杨鹰, 李海普, 满瑞林. 恒压过滤常数的实验数据处理[J]. 广州化工, 2018, 46(18): 113-115.	(中文期刊).
[6] 张习博. 基于Origin软件的化工原理实验曲线拟合方法与应用[J]. 粘接, 2019, 40(09): 122-126.	(中文期刊).
[7] 宋莎, 黎亚明, 王艳力, 等. 自制恒压过滤参数测定实验多功能设备的实践[J]. 实验技术与管理, 2015(06): 94-96+142.	(中文期刊).
[8] 吴燕翔, 王碧玉. 恒压过滤介质阻力分析[J]. 化工学报, 2004, 12(01): 33-36.	(中文期刊).
[9] 苏旭霞, 刘素楠, 管立新. 开展虚拟仿真实验，促进实验教学改革[J]. 科技广场, 2008(03): 252-254.	(中文期刊).
[10] 潘正官, 谢佑国. 自行研制实验设备创建高水平示范性实验室[J]. 实验室研究与探索, 2006, 25(09): 1152-1153.	(中文期刊).
[11] 胡芳, 赵亮方. 高校自制实验教学设备的体会[J]. 中国现代教育装备, 2011(15): 42-43.	(中文期刊).
[12] 廖庆敏, 秦钢年, 蒙艳玫. 把自制设备作为实验教学示范中心的特色[J].	(中文期刊).
[13] Nguyen, T. P. H.; Cai, Z.; Nguyen, K.; Keth, S.; Shen, N.; Park, M. Pre-processing Image using Brightening, CLAHE and RETINEX. \textit{arXiv} 2020, arXiv:2003.10822. https://doi.org/10.48550/arXiv.2003.10822	(英文期刊).
[14] Kryjak, T. ; Blachut, K.; Szolc, H.; Wasala, M. Real-Time CLAHE Algorithm Implementation in SoC FPGA Device for 4K UHD Video Stream. \textit{Electronics} 2022, 11(14), 2248. https://doi.org/10.3390/electronics11142248	(英文期刊).
[15] Mishra, A. Contrast Limited Adaptive Histogram Equalization (CLAHE) Approach for Enhancement of the Microstructures of Friction Stir Welded Joints. \textit{arXiv} 2021, arXiv:2109.00886. https://doi.org/10.48550/arXiv.2109.00886	(英文期刊).
[16] Akbari Sekehravani, E. ; Babulak, E.; Masoodi, M. Implementing canny edge detection algorithm for noisy image. \textit{Bulletin of Electrical Engineering and Informatics}, 2020, 9(4), 1404–1410. https://doi.org/10.11591/eei.v9i4.1837	(英文期刊).
[17] Agrawal, H. ; Desai, K. CANNY EDGE DETECTION: A COMPREHENSIVE REVIEW. \textit{International Journal of Technical Research \& Science}, 2024, 9(Spl), 27–35. https://doi.org/10.30780/specialissue-ISET-2024/023	(英文期刊).
[18] Jamil, N. ; Sembok, T.; Bakar, Z. Noise removal and enhancement of binary images using morphological operations. In \textit{Int Symp Inf Technol 2008 ITSim}, 2008, 3, 1-6. https://doi.org/10.1109/ITSIM.2008.4631954	(英文会议).
[19] Horebeek, J. ; Tapia-Rodriguez, E. The approximation of a morphological opening and closing in the presence of noise. \textit{Signal Processing}, 2001, 81, 1991-1995. https://doi.org/10.1016/S0165-1684(01)00060-3	(英文期刊).
[20] Olbrich, M. ; Riazy, L.; Kretz, T.; Leonard, T.; van Putten, D. S.; Bär, M.; Oberleithner, K.; Schmelter, S. Deep learning based liquid level extraction from video observations of gas–liquid flows. \textit{Int. J. Multiphase Flow}, 2022, 157, 104247. https://doi.org/10.1016/j.ijmultiphaseflow.2022.104247	(英文期刊).
[21] Dou, G. ; Chen, R.; Han, C.; Liu, Z.; Liu, J. Research on Water-Level Recognition Method Based on Image Processing and Convolutional Neural Networks. \textit{Water}, 2022, 14(12), 1890. https://doi.org/10.3390/w14121890	(英文期刊).
[22] Nicholaus, I. T.; Lee, J.-S.; Kang, D.-K. One-Class Convolutional Neural Networks for Water-Level Anomaly Detection. \textit{Sensors}, 2022, 22(22), 8764. https://doi.org/10.3390/s22228764	(英文期刊).
[23] Sun, Q. ; Zhou, W. X.; Fan, J. Adaptive Huber Regression. \textit{J. Am. Stat. Assoc.}, 2020, 115(529), 254-265. https://doi.org/10.1080/01621459.2018.1543124	(英文期刊).