import config
import re
from requests import Session
from robobrowser import RoboBrowser
from bs4 import BeautifulSoup
from werkzeug.contrib import limiter


FIELD_NAMES = { 
      "DOCUMENTO_ID"        : "Identificação"
     ,"DOCUMENTO_DATA"      : "Data de emissão"
     ,"AUTORIDADE_NOME"     : "Nome"
     ,"AUTORIDADE_FUNCAO"   : "Função"
     ,"REGISTRO"            : "Nº de registro"
     ,"REGISTRO_DATA"       : "Data de registro"
     ,"PROCEDIMENTO"        : "Procedimento"
    }

DADOS_LAUDO = {}

# ---------------- coleta o texto de um trecho com delimitação por strings -------------------
def get_text_from_trecho(trecho, string_de_busca, string_fim, offset_inicio = 0):
    sub_trecho = ""
    #if isinstance(trecho,tipo_tag etc etc etc 
    for tag in trecho:   #Substituir este laço por algo assim --> paragrafo = (parag in tag.get_text() for tag in trecho)
        if string_de_busca in tag.get_text():
            sub_trecho = tag.get_text()      
    return  sub_trecho[sub_trecho.find(string_de_busca) + len(string_de_busca) + offset_inicio: sub_trecho.find(string_fim):].lstrip()
    

def create_dict_from_resultset(resultset, fields):
    dict = {}
    for tag in resultset:    # modificar para algo assim --> field = ([f for field in fields] in str(tag.next_sibling.next_element)):
        for key in fields:
            if str(fields[key]).lstrip() in str(tag):
                dict[key] = str(tag.next_sibling).replace("\n","").lstrip()
    return dict


#------- LOGIN --------------------
session = Session()
session.verify = False
browser = RoboBrowser(session=session, parser="html5lib")
browser.open("https://ditec.pf.gov.br/sistemas/criminalistica/meus_dados.php")
form_login = browser.get_form()
form_login["usuario"].value = config.LOGIN["SISCRIM"]["USER"] 
form_login["senha"].value = config.LOGIN["SISCRIM"]["PASS"]
browser.submit_form(form_login)

#------- PRENCHE MATERIAL --------------------
numero_material = "846/2017"
form_mat1 = browser.get_form()
form_mat1["tipo_busca"].value = "numero_material" 
form_mat1["numero_busca"].value = numero_material
browser.submit_form(form_mat1) 

#------- NAVEGA P/ MATERIAL --------------------
browser.follow_link(browser.get_link(str(numero_material)))

#------- COLETA A DESCRICAO DO MATERIAL -------------------- 
trecho = browser.parsed.find_all("td", id="area_central")
descricao_material = get_text_from_trecho(trecho,"Descrição","Lacre",4) 
#print(descricao_material)

#------------DESCOBRE O NUMERO DA REFERENCIA(REGISTRO)------------
link_referencia = browser.get_link(str("Memorando"))  #Na criação das classes modificar este teste para dentro dos membros de uma lista: Memos, REs etc
descricao_referencia = link_referencia.get_text().lstrip()  
#print(descricao_referencia)

#------- NAVEGA P/ REGISTRO(MEMORANDO) --------------
browser.follow_link(link_referencia)

#------- INICIA PREENCHIMENTO DOS DADOS DO LAUDO --------------
todos_os_rotulos = browser.find_all("span", class_="rotulo", limit=15) 
DADOS_LAUDO = create_dict_from_resultset(todos_os_rotulos, FIELD_NAMES)

#------- NAVEGA P/ CRIAÇÃO DO LAUDO --------------
link_elaborar_laudo = browser.get_link("Elaborar documento científico relacionado")
browser.follow_link(link_elaborar_laudo)

#------- PREENCHE OS DADOS PARA CRIAÇÃO DO LAUDO - #FORM_1# --------------
#attributes_dictionary = browser.parsed.find('form').attrs
#print(attributes_dictionary)


'''
Muitos campos hidden.
Testar o preenchimento dos campos hidden da mesma forma que o html preenche.
    Coletar o codigo_objeto_pai a partir do endereço da página.
        . Pegar na beutifullsoup ou no link anterior que encaminhou para cá.
    Preencher todos os campos hidden da mesma forma que o html faz.
    Testar o submit.

'''
form1_laudo = browser.get_form()
form1_laudo["codigo_tipo_documento"].value = "Laudo" 
form1_laudo["codigo_titulo_laudo"].value = "Laudo de Exame de Dispositivo de Armazenamento Computacional"
#-- Hidden fields -------------------
form1_laudo["codigo_tipo_documento"].value = "Laudo"


form1_laudo["codigo_documento_interno"]=None
form1_laudo["passo"].value="2"
form1_laudo["data_emissao"].value=""
form1_laudo["codigo_finalidade_documento"].value="4"
form1_laudo["urgencia"].value="1"
form1_laudo["numero_copia"].value="0"
form1_laudo["entrada_saida"].value="S"
form1_laudo["codigo_objeto_pai"].value="35990950"
form1_laudo["sigla_unidade_emissora"].value=""
form1_laudo["usuario_criacao"].value=""
form1_laudo["codigo_documento_elaborado"].value=""
form1_laudo["codigo_unidade_registro"].value=""

'''
    <tbody><tr class="oculto">
        <td colspan="2">form1_laudo["posicaox" id="posicaox"].value="">
    </td></tr>
    <tr class="oculto">
        <td colspan="2">form1_laudo["posicaoy" id="posicaoy"].value="">
'''

'''
  <input type="hidden" name="codigo_documento_interno" value="">
  <input type="hidden" name="passo" value="2">
  <input type="hidden" name="data_emissao" value="">
  <input type="hidden" name="codigo_finalidade_documento" value="4">
  <input type="hidden" name="urgencia" value="1">
  <input type="hidden" name="numero_copia" value="0">
  <input type="hidden" name="entrada_saida" value="S">
  <input type="hidden" name="codigo_objeto_pai" value="35990950">
  <input type="hidden" name="sigla_unidade_emissora" value="">
  <input type="hidden" name="usuario_criacao" value="">
  <input type="hidden" name="codigo_documento_elaborado" value="">
  <input type="hidden" name="codigo_unidade_registro" value="">
    <tbody><tr class="oculto">
        <td colspan="2"><input type="hidden" name="posicaox" id="posicaox" value="">
    </td></tr>
    <tr class="oculto">
        <td colspan="2"><input type="hidden" name="posicaoy" id="posicaoy" value="">
    </td></tr>
'''



browser.submit_form(form1_laudo) 

#------- PREENCHE OS DADOS PARA CRIAÇÃO DO LAUDO - #FORM_2# --------------
#form2_laudo = browser.get_form()
#form2_laudo["codigo_tipo_documento"].value = "Laudo" 
#browser.submit_form(form1_laudo) 


#trecho = browser.parsed.find_all("td", id="area_central")
#trecho = browser.parsed.select_one("td[id=area_central]")
#trecho_registro = browser.parsed.find_all("span", "Registro")

#------------------
#def find_class(classe, valor):
#    return classe and not re.compile(valor).search(classe)
#-----------------------

#def find_tag(tag):
#    return tag and not re.compile("Descrição").search(tag)
#soup.find_all(tag=find_tag)

