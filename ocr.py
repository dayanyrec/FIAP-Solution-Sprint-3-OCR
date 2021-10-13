import pytesseract as ocr
from PIL import Image
import cv2 as cv
import numpy as np
import re
import pprint as pp
from pathlib import Path

#imgName = 'img/helloworld.jpg'
#imgName = 'img/cupom1-amarelo.jpg'
#imgName = 'img/noisybg.png'
#imgName = 'img/cupom2-branco-rot.jpg'
#imgName = 'img/condor1.jpeg'
#imgName = 'img/mc1.jpeg'
imgName = 'img/cupom.jpg'
#imgName = 'img/condor3.jpeg'

# Lê a imagem em array (colorida)
# img = cv.imread(imgName, cv.IMREAD_COLOR)

#text = ocr.image_to_string(Image.open(imgName), lang='eng')
#print("=================== ORIGINAL ==================")
#print(text)
#print("===============================================")

def image_save(img, name_extension = "new"):
    Path("output/").mkdir(parents=False, exist_ok=True)
    new_name = "output/image_output-" + name_extension + ".png"
    cv.imwrite(new_name, img)
    return new_name

def image_rotation_adjust(img):
    # Converte a imagem para preto e branco 
    (img_binary, new_name) = image_to_binary(img)
    # Monta o array de coordenadas dos pixels pretos, ou seja, com valor zero
    # https://numpy.org/doc/stable/reference/generated/numpy.column_stack.html
    coords = np.column_stack(np.where(img_binary == 0))
    # Retorna no último índice do array o angulo do mínimo retângulo de borda localizado na imagem
    # Retorno do tipo RotatedRect()
    # [0] center	The rectangle mass center.
    # [1] size	Width and height of the rectangle.
    # [2] angle	The rotation angle in a clockwise direction. When the angle is 0, 90, 180, 270 etc., the rectangle becomes an up-right rectangle.
    # https://docs.opencv.org/4.1.1/db/dd6/classcv_1_1RotatedRect.html#aba20dfc8444fff72bd820b616f0297ee
    angle = cv.minAreaRect(coords)[-1]
    print(angle)

    # Baseado no ângulo encontrado, calcula quantos graus serão necessário de ajuste
    # Rotação para a esquerda é um número positivo
    # Rotação para a direita é um número negativo
    # Transferidor online para conferência https://www.ginifab.com/feeds/angle_measurement/online_protractor.pt.php
    if angle < 90 and angle > 3:
        angle = 90 - angle
    elif angle < 3:
        angle = -angle
    else:
        angle = -(angle - 90)
    #print(angle)

    # Aplica transofrmação geométrica do tipo Affine na imagem
    # https://docs.opencv.org/master/da/d6e/tutorial_py_geometric_transformations.html
    # https://docs.opencv.org/master/da/d54/group__imgproc__transform.html#ga0203d9ee5fcd28d40dbc4a1ea4451983
    # A função whapAffine transforma a imagem utilizando uma matriz
    h, w = img.shape[:2]
    center = (w//2, h//2)
    print(angle)
    M = cv.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv.warpAffine(img, M, (w, h), flags=cv.INTER_CUBIC, borderMode=cv.BORDER_REPLICATE)
    image_save(rotated_image, "rotated")
    return rotated_image

def image_filter(img, filter):
    if filter == "gaussian":
        img = cv.GaussianBlur(img,(5,5),0)
    elif filter == "median":
        img = cv.medianBlur(img,5)
    elif filter == "denoise":
        img = cv.fastNlMeansDenoising(img,None,7,7,21)
    elif filter == "bilateral":
        img = cv.bilateralFilter(img,9,30,30)
    new_name = image_save(img, filter)
    return (img, new_name)

def image_to_grayscale(img):
    # Converte a imagem para escala de cinza
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    new_name = image_save(img, "grayscale")
    return (img, new_name)

def image_to_binary(img):
    # Converte a imagem para escala de cinza
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Necessária eliminação de ruído antes da aplicação do threshold adaptativo
    img = cv.bilateralFilter(img,17,70,70)
    # Aplica threshold gaussiano adaptativo para conversão em preto e branco   
    img = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,9,2)
    img = cv.medianBlur(img,9)
    new_name = image_save(img, "binary")
    return (img, new_name)

# image_to_data retorna uma saída no formato TSV com o cabeçalho abaixo:
# ['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'conf', 'text']
# https://www.tomrochette.com/tesseract-tsv-format
# level: hierarchical layout (a word is in a line, which is in a paragraph, which is in a block, which is in a page), a value from 1 to 5
#     1: page
#     2: block
#     3: paragraph
#     4: line
#     5: word
# page_num: when provided with a list of images, indicates the number of the file, when provided with a multi-pages document, indicates the page number, starting from 1
# block_num: block number within the page, starting from 0
# par_num: paragraph number within the block, starting from 0
# line_num: line number within the paragraph, starting from 0
# word_num: word number within the line, starting from 0
# left: x coordinate in pixels of the text bounding box top left corner, starting from the left of the image
# top: y coordinate in pixels of the text bounding box top left corner, starting from the top of the image
# width: width of the text bounding box in pixels
# height: height of the text bounding box in pixels
# conf: confidence value, from 0 (no confidence) to 100 (maximum confidence), -1 for all level except 5
# text: detected text, empty for all levels except 5

def image_ocr_data(image_name):
    text = ocr.image_to_data(Image.open(image_name), lang='por')
    text = text.lower()
    #print("================== IMAGE DATA =================")
    #print(text)
    lines = text.splitlines()
    result = []
    header_len = len(lines[0].split())
    for line in lines:
        line = line.split()
        #if ((line[-1] != '-1') and (len(line) == header_len)):
        result.append(line)
        print(line)
    #pp.pprint(result)
    return result

def image_draw_word_spaces(img, image_data):
    for word in image_data[1:]:
        leftCorner = int(word[6])
        topCorner = int(word[7])
        width = int(word[8])
        height = int(word[9])
        rightCorner = leftCorner + width
        bottomCorner = topCorner + height
        cv.rectangle(img,(leftCorner,topCorner),(rightCorner,bottomCorner),(0,0,255),1)
        image_save(img, "drawn")
    return img

def image_find_textarea(img, image_data):

    header_len = len(image_data[0])

    for word in image_data[1:]:
        if ((word[-1] != '-1') and int(word[0]) == 5) and (len(word) == header_len):
            most_top_point = int(word[6])
            most_left_point = int(word[7])
            most_right_point = most_left_point + int(word[9]) # Adiciona a largura ao ponto esquerdo para calcular o ponto direito
            most_bottom_point = most_top_point + int(word[8]) # Adiciona a altura ao ponto superior para calcular o ponto inferior
            break

    for word in image_data[1:]:
        if ((word[-1] != '-1') and int(word[0]) == 5) and (len(word) == header_len):
            leftCorner = int(word[6])
            topCorner = int(word[7])
            width = int(word[8])
            height = int(word[9])
            rightCorner = leftCorner + width
            bottomCorner = topCorner + height

            if leftCorner < most_left_point:
                most_left_point = leftCorner
            if topCorner < most_top_point:
                most_top_point = topCorner
            if rightCorner > most_right_point:
                most_right_point = rightCorner
            if bottomCorner > most_bottom_point:
                most_bottom_point = bottomCorner

    cv.rectangle(img,(most_left_point-11,most_top_point-11),(most_right_point+11,most_bottom_point+11),(0,0,255),1)

    text_area_coord = {}
    text_area_coord['left'] = most_left_point
    text_area_coord['top'] = most_top_point
    text_area_coord['right'] = most_right_point
    text_area_coord['bottom'] = most_bottom_point

    #pp.pprint(text_area_coord)
    
    image_save(img, "text_area")
    return (img, text_area_coord)

def image_crop(img, image_coord):
    if(image_coord['left'] >= 10 and image_coord['top'] >= 10):
        left = image_coord['left']-10
        top = image_coord['top']-10
        right = image_coord['right']+10
        bottom = image_coord['bottom']+10
        cropped_image = img[top:bottom, left:right]
        new_name = image_save(cropped_image, "cropped")
    else:
        cropped_image = img
        new_name = image_save(cropped_image, "cropped")
    return (cropped_image, new_name)

# Abre janela com a imagem já aberta pelo OpenCV
def image_show(img, name='Window'):
    # Cria uma janela com o nome passado como parâmetro
    cv.namedWindow(name)
    # Insere a imagem liga dentro da janela criada
    cv.imshow(name, img)
    # Espera que seja pressionada qualquer tecla para fechar a janela
    cv.waitKey()
    cv.destroyAllWindows()

# Definição do cabeçalho
# ['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'conf', 'text']
def structure_image_data(image_data):
    blocks = {}
    header_len = len(image_data[0])
    for word in image_data[1:]:
        if ((word[-1] != '-1') and int(word[0]) == 5) and (len(word) == header_len):
            block_num = word[2]
            par_num = word[3]
            line_num = word[4]
            word_num = word[5]
            text = word[-1]
            try:
                blocks[block_num]
            except:
                blocks[block_num] = {}
            try:
                blocks[block_num][par_num]
            except:
                blocks[block_num][par_num] = {}
            try:
                blocks[block_num][par_num][line_num]
            except:
                blocks[block_num][par_num][line_num] = {}
            blocks[block_num][par_num][line_num][word_num] = text
    #pp.pprint(blocks)
    return blocks

def rebuild_image_text(blocks):
    text = ""
    line_list = []
    for block_num, lines in blocks.items():
        for par_num, pars in lines.items():
            for line_num, words in pars.items():
                for word_num, word in words.items():
                    text = text + " " + word
                line_list.append(text)
                #print(text)
                text = ""
    return line_list

def search_text(line_list, text):
    k = 0
    for line in line_list:
        match = re.search(text, line)
        if match:
            #print("ENCONTRADO: " + str(k) + " - " + match.group(1))
            # print(line)
            break
        k = k + 1
    return (k, line)




# Localiza o cabeçalho de produtos
# iten cod. desc. otd. um. vl.unit st ul.item
# Considera que os produtos serão listados após o cabeçalho com um contador de 3 dígitos
def find_products(line_list):
    try:
        (index, text) = search_text(line_list, "(iten|item|cod\.|desc\.)")
        index = index + 1
    except:
        index = 0

    products = []
    for line in line_list[index:]:
        product_num = line.split()[0]
        if re.match('^[0-9]{3}$', product_num):
            product = line + line_list[index + 1]
            products.append(product)
        index = index + 1
    return products

def find_total(line_list):
    (index, text) = search_text(line_list, "(valor|total)(.*)(rs|r\$|\$)(\D*)([0-9]+[,\.][0-9]{2})$")
    return text

def find_customer(line_list):
    (index, text) = search_text(line_list, "((cpf)|(\d{1,3}[,\.]\d{3}[,\.]\d{3}[-]\d{1,2}))")
    customer = text + line_list[index + 1]
    return customer




# 1) Leitura da imagem original
img_original = cv.imread(imgName)
# 2) Ajuste de rotação
img = image_rotation_adjust(img_original)
# 3) Remoção de ruído
(img, img_new_name) = image_filter(img, "bilateral")
(img, img_new_name) = image_filter(img, "denoise")
# 4) Transformação para escala de cinza
(img, img_new_name) = image_to_grayscale(img)

# 5) Leitura de todos os dados do OCR
img_data = image_ocr_data(img_new_name)
(img, textarea_coord) = image_find_textarea(img, img_data)
(img, img_new_name) = image_crop(img, textarea_coord)
img_data = image_ocr_data(img_new_name)
#pp.pprint(img_data)
# Passo opcional de verificação. Desenha retângulos em volta das palavras reconhecidas
image_draw_word_spaces(img, img_data)
# 6) Monta o Dict estruturado dos dados do OCR
img_data_structured = structure_image_data(img_data)
pp.pprint(img_data_structured)
# 7) Reconstrói o texto da imagem em linhas
line_list = rebuild_image_text(img_data_structured)
pp.pprint(line_list)

#match = re.match('^(.*)(cnpj|cmpj|cnpi|cmpi)(\D*)([\d\.\,/-]+)\n',text)
#if match:
#    print("Estabelecimento: " + str(match.group(1)).title())
try:
    company = line_list[0].title()
    print("ESTABELECIMENTO: " + company)
except:
    print('Erro ao localizar o estabelecimento')
try:
    total = find_total(line_list)
    print("VALOR TOTAL: " + total)
except:
    print('Erro ao localizar o valor total')
try:
    customer = find_customer(line_list)
    print("CLIENTE: "+ customer)
except:
    print('Erro ao localizar o cliente')
try:
    products = find_products(line_list)
    if products:
        print("PRODUTOS")
        for p in products:
            print(p)
    else:
        print("Nenhum produto identificado")
except:
    print('Erro ao localizar itens')









#match = re.search('(valor|total)(.*)(rs|r\$|\$)(\D*)([0-9]+[,\.][0-9]{2})\n',text)
#if match:
#    print("Valor Total: R$ " + match.groups()[-1])
#
#match = re.search('(cpf|consumidor)(.*)\n(.*)',text)
#if match:
#    print("Consumidor: " + str(match.group(3)).title())


# Mostra as linguagens suportadas pelo ocr
#print(ocr.get_languages(config=''))