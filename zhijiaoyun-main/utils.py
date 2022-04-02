import muggle_ocr
  
def captcha(imagePath):

    sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)

    with open(imagePath, 'rb') as f:
        b = f.read()
    
    res = sdk.predict(image_bytes=b)

    return res
    

if __name__ == '__main__':
    print('请运行mian.py文件！')


