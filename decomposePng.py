#!/usr/bin/python3
#coding=utf8

# 通过 Json 配置文件分解 PNG 合图。


import sys, os
from tkinter import *
import tkinter.filedialog
from urllib.request import urlretrieve
import _thread
from PIL import Image
import json

# 选择图片
def selectImage():

    fileName = tkinter.filedialog.askopenfilename(title = '选择合图', filetypes = [('.png', '*.png')])
    if fileName != '':
        updateEntryText(imgEntry, fileName)

# 选择 Json
def selectJson():

    fileName = tkinter.filedialog.askopenfilename(title = '选择 JSON 配置文件', filetypes = [('.json', '*.json')])
    if fileName != '':
        updateEntryText(jsonEntry, fileName)

# 选择分解图片的保存路径
def selectOutDir():

    selectDir = tkinter.filedialog.askdirectory()
    if selectDir != '':
        updateEntryText(outDirEntry, selectDir)

# 修改 Entry 组件显示的文字
def updateEntryText(entry, text):

    entry.delete(0, END)
    entry.insert(0, text)

# 插入显示分解信息 。
def insertDecomposeInfo(text, fg = 'black'):

    decomposeInfoListBox.insert(END, text)
    decomposeInfoListBox.itemconfig(END, fg = fg, selectbackground = 'white', selectforeground = fg)

# 清理显示的分解信息的。
def clearDecomposeInfo():

    decomposeInfoListBox.delete(0, END)

# 分解图片
def decomposeImage():

    global imgEntry
    global jsonEntry
    global outDirEntry

    decomposeButton.state = DISABLED

    clearDecomposeInfo()
	
    # ---------- 检查用户输入的数据 -----------

    decomposeEnable = True

    imgPath = imgEntry.get()
    imgPathError = ''
    if imgPath == '':
        imgPathError = '未选择图片'
    elif not imgPath.startswith('http') and not os.path.exists(imgPath):
        imgPathError = '指定的图片文件不存在'
    if not imgPathError == '':
        insertDecomposeInfo(imgPathError, fg = 'red')
        decomposeEnable = False

    jsonPath = jsonEntry.get()
    jsonPathError = ''
    if jsonPath == '':
        jsonPathError = '未选择 JSON 配置'
    elif not jsonPath.startswith('http') and not os.path.exists(jsonPath):
        jsonPathError = '指定的 JSON 文件不存在'
    if not jsonPathError == '':
        insertDecomposeInfo(jsonPathError, fg = 'red')
        decomposeEnable = False
	
    outDir = outDirEntry.get()
    outDirError = ''
    if outDir == '':
        outDirError = '未选择保存路径'
    elif not os.path.exists(outDir):
        os.makedirs(outDir)
        outDirError = '指定的保存路径不存在'
    if not outDirError == '':
        insertDecomposeInfo(outDirError, fg = 'red')
        decomposeEnable = False

    if not decomposeEnable:
        decomposeButton.state = NORMAL
        return

    # ---------- 下载文件 -----------
    def download():
        if imgPath.startswith('http'):
            insertDecomposeInfo('正在下载图片...')
            imgFilePath = downloadFile(imgPath, outDir + os.sep + '0_raw')
            insertDecomposeInfo('图片下载完成')
        else:
            imgFilePath = imgPath

        if jsonPath.startswith('http'):
            insertDecomposeInfo('正在下载 JSON 文件...')
            jsonFilePath = downloadFile(jsonPath, outDir + os.sep + '0_raw')
            insertDecomposeInfo('JSON 文件下载完成')
        else:
            jsonFilePath = jsonPath

        decompose(imgFilePath, jsonFilePath, outDir)

        decomposeButton.state = NORMAL

    _thread.start_new_thread(download, ())


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False

# 分解
def decompose(imgFilePath, jsonFilePath, outDir):

    insertDecomposeInfo('正在分解图片...')
    insertDecomposeInfo(imgFilePath)

    rawImg = Image.open(imgFilePath)
    imgFrames = json.loads(open(jsonFilePath).read())['frames']
    insertDecomposeInfo(imgFrames)
    for frame in imgFrames:
        if is_json(frame):
            x = frame['frame']['x']
            y = frame['frame']['y']
            w = frame['frame']['w']
            h = frame['frame']['h']
            childImg = rawImg.crop((x, y, x + w, y + h))
            childImg.save(outDir + os.sep + frame['filename'])
        else:
            element = imgFrames[frame]
            x = element['frame']['x']
            y = element['frame']['y']
            w = element['frame']['w']
            h = element['frame']['h']
            childImg = rawImg.crop((x, y, x + w, y + h))
            childImg.save(outDir + os.sep + frame + ".png")

    insertDecomposeInfo('图片分解完成')

# 下载文件
def downloadFile(url, saveDir):
    os.makedirs(saveDir, exist_ok = True)
    fileName = saveDir + os.sep + os.path.basename(url)
    urlretrieve(url, fileName)
    return fileName

def showGUI():

    root = Tk()

    root.title("合图分解")
    root.resizable(False, False)

    global imgEntry
    global jsonEntry
    global outDirEntry
    global decomposeButton
    global decomposeInfoListBox

    promptRow = 0
    imgRow = 1
    jsonRow = 2
    outDirRow = 3
    decomposeRow = 4
    decomposeInfoFrameRow = 5

    Label(root, text = '使用网络或者本地数据均可。', fg = 'gray').grid(row = promptRow, column = 0, columnspan = 3, sticky = 'w')

    Label(root, text = '合图文件：').grid(row = imgRow, column = 0)
    imgEntry = Entry(root, width = 50)
    imgEntry.grid(row = imgRow, column = 1)
    Button(root, text = '选择', command = selectImage).grid(row = imgRow, column = 2)

    Label(root, text = 'JSON文件：').grid(row = jsonRow, column = 0)
    jsonEntry = Entry(root, width = 50)
    jsonEntry.grid(row = jsonRow, column = 1)
    Button(root, text = '选择', command = selectJson).grid(row = jsonRow, column = 2)

    Label(root, text = '保存到：').grid(row = outDirRow, column = 0)
    outDirEntry = Entry(root, width = 50)
    outDirEntry.grid(row = outDirRow, column = 1)
    Button(root, text = '选择', command = selectOutDir).grid(row = outDirRow, column = 2)

    decomposeButton = Button(root, text = '分解合图', command = decomposeImage)
    decomposeButton.grid(row = decomposeRow, column = 0, columnspan = 3)

    decomposeInfoFrame = Frame(root)
    decomposeInfoFrame.grid(row = decomposeInfoFrameRow, column = 0, columnspan = 3, sticky = N + S + E + W)
    decomposeInfoFrame.grid_propagate(False)

    Scrollbar(decomposeInfoFrame).pack(side = LEFT)
    scrollbar = Scrollbar(decomposeInfoFrame)
    scrollbar.pack(side = RIGHT, fill = Y)
    decomposeInfoListBox = Listbox(decomposeInfoFrame, yscrollcommand = scrollbar.set, activestyle = NONE)
    decomposeInfoListBox.pack(side = LEFT, fill = BOTH, expand = True)
    scrollbar.config(command = decomposeInfoListBox.yview)

    root.update_idletasks()
    x = root.winfo_screenwidth() / 2 - root.winfo_reqwidth() / 2
    y = root.winfo_screenheight() / 2 - root.winfo_reqheight() / 2
    root.geometry('+%d+%d' % (x, y))

    mainloop()

if __name__ == '__main__':
    showGUI()
