# FIAP-Solution-Sprint-3-OCR  

## Setup em SO Windows  

1. Instale o Python:  
https://www.python.org/downloads/

2. Instale uma IDE, por exemplo, o Visual Studio Code:  
https://code.visualstudio.com/download

3. Crie uma pasta para o projeto em qualquer lugar do seu Windows

4. Dentro do Visual Studio Code, selecione a opção para abrir uma pasta e abra a pasta que você criou.

5. Crie um novo arquivo, com qualquernome.py

6. O VS Code irá sugerir a instalação da extensão para Pyhton, instale.

7. Abra um terminal dentro do VS Code mesmo e instale pytesseract com o comando abaixo:  
`pip install pytesseract`

    A documentação do Pytesseract está disponível em:  
https://pypi.org/project/pytesseract/

8. Instale o Google OCR Tesseract:  
https://github.com/UB-Mannheim/tesseract/wiki

9. Adicione uma variável de sistema na variável PATH, para isso:  
    9.1. Digite na busca do Windows: Editar as variáveis de ambiente do sistema  
    9.2. Clique em Variáveis de Ambiente. Na tabela de baixo "Variáveis do Sistema", localize a variável "Path", selecione-a e clique em Editar.
    9.3. Clique em "Novo" e adicione o caminho onde você instalou o Tesseract OCR, se foi no caminha padrão será isso: `C:\Program Files\Tesseract-OCR\`

10. Reinicie seu terminal, fechando e abrindo novamente o VS Code.

## Verificação da instalação  

1. Cole o seguinte script no seu arquivo python:

```
import pytesseract as ocr
from PIL import Image

phrase = ocr.image_to_string(Image.open('phrase.jpg'), lang='eng')

print(phrase)
```

2. Salve na mesma pasta do script alguma imagem que contenha um texto, com o nome de phrase.jpg

3. Clique com o botão direito em qualquer lugar do seu script dentro do VS Code e clique na opção "Executar arquivo no terminal"

4. O script deve executar e texto contido na imagem deve aparecer no terminal

## Adicionando português no Tesseract

1. Baixe o arquivo https://github.com/tesseract-ocr/tessdata/blob/master/por.traineddata  

2. Adicione-o na pasta `C:\Program Files\Tesseract-OCR\tessdata`

3. Para verificar as linguagens suportadas pelo ocr utilize:  
```
print(ocr.get_languages(config=''))
# ['eng', 'osd', 'por'] <- output do comando
```

## Instalação do OpenCV (lib para manipulação de imagens)

1. Instale o matplotlib  
`pip install matplotlib`

2. Instale o opencv-python  
`pip install opencv-python`

3. Baixe o OpenCV: https://opencv.org/releases/.  
Documentação em:  
- https://docs.opencv.org/master/
- https://docs.opencv.org/master/d5/de5/tutorial_py_setup_in_windows.html

## Links úteis

- https://techtutorialsx.com/2019/04/13/python-opencv-converting-image-to-black-and-white/  
- https://docs.opencv.org/3.4/d5/d69/tutorial_py_non_local_means.html  
- https://stackoverflow.com/questions/62042172/how-to-remove-noise-in-image-opencv-python  

- Processamento de imagens em Python com OpenCV: https://docs.opencv.org/master/d2/d96/tutorial_py_table_of_contents_imgproc.html  

- Documentação sobre transformação geométrica com OpenCV em Python,usado para executar a rotação: https://docs.opencv.org/master/da/d6e/tutorial_py_geometric_transformations.html


## Extra  

Instalação das dependências utilizando virtual environment:  
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```