# Thesis_Scripts_PositionalAccuracy
Scripts para avaliação da Acurácia Posicional de dados geoespaciais no software QGIS 3.18

Para obter os resultados é necessário inserir o script no console Python do software QGIS. Será aberta uma janela para a inserção dos arquivos vetoriais e da escala desejada para as análises.


PARTE 1 - CQDG_points_features

Com esta ferramenta é possivel avaliar a Acurácia Posicional de feições pontuais no software QGIS com base na Especificação Técnica para Controle de Qualidade de Dados Geoespaciais:

- 90% das Distâncias Euclidianas menores que o  valor do PEC-PCD na classe da escala inserida;

- Erro Médio Quadrático das Distâncias Euclidianas menor ou igual ao valor do Erro Padrão estabelecido para o PEC-PCD na classe da escala inserida.

Requisitos para realização das análises: 

- Dois conjuntos de arquivos vetoriais de feições pontuais com um atributo "ID" que identifique as feições homologas em cada uma;

- Arquivos vetoriais devem estar projetados em UTM;

- Inserir a escala desejada para as análises. 

Resultados Obtidos:

- Distância Euclidiana e Erro Médio Quadrático de cada feição;

- Classes A, B, C e D do PEC-PCD e a mensagem de 'Aceito' ou 'Rejeitado', para cada uma delas, de acordo com as condicionantes descritas. 



