import os,glob,copy
import numpy as np
from PIL import Image
class NazoFramer:
    """問題画像を任意の枠(透過png)に当てはめるためのクラスです。
    setFrame(framePath)で枠を、setResultDir()で出力先を指定。
    コンストラクタでもできます。
    setPositonで位置を調整してください
    Attributes:
        margin(int):0ならピッチリリサイズ。問題画像と枠との距離のうち最も狭い部分の距離。
        bottom(int):marginで設定された場所(中央)から下にずらす。初期値は0
        right(int):marginで設定された場所(中央)から右にずらす。初期値は0
        resultDir(str):出力先のディレクトリへのパス。末尾の"/"はあってもなくても可
        frameImage:枠の画像データ。PIL型
        backgroundImage:枠と同サイズの白い長方形。PIL型        
    """
    def __init__(self,framePath="",resultPath = "result/"):
        self.margin = 0
        self.bottom = 0
        self.right = 0
        self.framePath = ""
        self.frameImage = []
        self.backgroundImage = Image.new("RGB", (512, 512), (255, 255, 255))
        self.setResultDir(resultPath)
        if framePath:
            self.setFrame(framePath)    

    def setFrame(self,framePath):
        """枠の再設定を行います。
        Args:
            framePath(str): 枠のある画像へのパスです。透過pngにしないとバグります。
        """
        #Frameを改めて設定/変更する
        self.frameImage = Image.open(framePath) 
        self.frameW,self.frameH = self.frameImage.size
        self.backgroundImage = Image.new("RGB", (self.frameW, self.frameH), (255, 255, 255))
        if self.framePath:
            print(f"枠の画像が {framePath} に変更されました")
        else:
            print(f"枠の画像が {framePath} に設定されました")
        self.framePath = framePath
        return

    def setResultDir(self,resultDir):
        """出力先の設定です。
        Args:
            resultDir(str): 出力先ディレクトリの相対/絶対パスを入力してください。
        """
        if resultDir.endswith("/"):
            self.resultDir = resultDir.rstrip("/")

    def setPosition(self,margin=None,right=None,bottom=None):
        """うまいこと配置場所を設定します。コンストラクタからはここはいじれないので手間ですが呼び出してください。
        """
        if margin is not None:
            self.margin = margin
        if right is not None:
            self.right = None
        if bottom is not None:
            self.bottom = bottom

    def applyTemplate(self,imagePath,resultDir="",margin=None,right=None,bottom=None,fileName=None):
        """入力されたimagePathについて枠を当てはめた画像を出力します。
        出力先ディレクトリがなければ作ります。
        「問題画像を中央に配置したのち、枠との最短距離がmarginになるまで縮小。それをbottomだけ下に、rightだけ右に動かしたもの」が出力されます。
        変数のmargin,right.bottom
        Args:
            margin(int): 枠の画像との距離です。**この処理だけに反映されます。**
            right(int): 右方向へのずれです。**この処理だけに反映されます。**
            bottom(int): 下方向へのずれです。 **この処理だけに反映されます。**
            fileName(str): 出力後のファイル名です。入力しなければ元ファイルと同じです。
        """
        if resultDir:
            self.setResultDir(resultDir)
        resultDir = self.resultDir
        #right,bottomの取得(設定がなければデフォルト)
        if margin is None:
            margin = self.margin
        if right is None:
            right = self.right
        if bottom is None:    
            bottom = self.right
        if fileName is None:
            fileName = os.path.basename(imagePath)

        #出力先ディレクトリの作成
        os.makedirs(resultDir,exist_ok=True)

        resultPath = resultDir + "/" + fileName
        #調整可能ステータス：margin,bottom,right
        BG = copy.deepcopy(self.backgroundImage)
        frame = copy.deepcopy(self.frameImage)
        content = Image.open(imagePath)
        if self.frameW is None:
            print("フレームが設定されていません") 
            return
        frameW,frameH = copy.deepcopy([self.frameW,self.frameH])
        contentW,contentH = content.size
        if contentH/contentW >= frameH/frameW:
            #問題が枠より縦長なら縦を基準に
            resizedContentH = frameH - margin * 2
            resizedContentW = int(resizedContentH*contentW/contentH)
            Start = ((frameW-resizedContentW)//2 + right, margin + bottom)
            #marginがダメだったらこことelseの縦とか横に固定値を足し引き
        else:
            #問題が枠より横長なら枠の横を基準に
            resizedContentW = frameW - margin * 2
            resizedContentH = int(resizedContentW*contentH/contentW)
            Start = (margin + right, (frameH-resizedContentH)//2 + bottom)
        #枠に合わせて問題画像を変形
        bottom = content.resize((resizedContentW,resizedContentH))
        BG.paste(bottom,Start)
        #ここ第三引数のpasteいらなくね？
        BG.paste(frame,(0,0),frame)
        BG.save(resultPath)
        print(f"{resultPath} に画像が保存されました")

help(FrameAdapter.applyTemplate)