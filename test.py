import numpy as np
import pandas as pd

filepath = r"C:\Users\a4841\OneDrive\桌面\實驗室\Fe2WO6數據\散射.xlsx"
df = pd.read_excel(filepath, sheet_name='工作表1')

DegreeData = df['2thelta'] # 假设 '2thelta' 是第一列

print(DegreeData)

InputDegreeMin = input("輸入最小角度:")
InputDegreeMax = input("輸入最大角度:")
DegreeMask = (DegreeData >= float(InputDegreeMin)) & (DegreeData <= float(InputDegreeMax))

FilteredData = DegreeData[DegreeMask]

TemperatureData = df.columns[1:].to_list() # 溫度並轉成列表

print(TemperatureData)
IntergrateData = [] # 用於存儲每個溫度的積分結果

# 每個溫度都進行同樣的計算

for temp in TemperatureData:
    IntensityData = df[temp][DegreeMask] # 每個溫度的強度數據
    slope = (IntensityData.iloc[-1] - IntensityData.iloc[0]) / (FilteredData.iloc[-1] - FilteredData.iloc[0])
    intercept = IntensityData.iloc[0] - slope * FilteredData.iloc[0]
    LinearBackground = slope * FilteredData + intercept
    SubstractedIntensity = IntensityData - LinearBackground
    # 積分
    Integral = np.trapz(SubstractedIntensity, FilteredData)
    IntergrateData.append(Integral)
    print(f"Temperature: {temp}, Integral: {Integral}")

result = pd.DataFrame({'Temperature': TemperatureData, 'Integral': IntergrateData})
result.to_csv(r"C:\Users\a4841\OneDrive\桌面\實驗室\Fe2WO6數據\積分結果.csv", index=False)

