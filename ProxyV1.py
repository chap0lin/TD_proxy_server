import socket
import thread
import string
import binascii
import time

URL_cache = []#vetor de URLs armazenados na cache
Dados_cache = []#vetor de dados armazenados na cache
n_url=0#Numero de sites armazenados na cache

def insere_log(site,mensagem):
    arq = open('/home/uwsim/Downloads/LOG.txt', 'a') 
    arq.write('Data: ')
    historico = time.strftime("%b %d %Y %H:%M:%S") 
    arq.write(historico)
    arq.write(' para ')
    arq.write(site)
    arq.write(' - ')
    arq.write(mensagem) 
    arq.close()


def mainfunct(mainsocket): #Funcao principal (thread)
    while 1:
        global n_url
        global URL_cache
        global Dados_cache
        data = mainsocket.recv(2048) #recebe a requisicao do usuario
        if not data: break
        aux = data.split('\n')
        site = (aux[1].split())[1] #separa o site desejado
        print site
	flag=0 #flag de comparacao para Whitelist, Blacklist e Denyterms
        tem_cache=0#flag da cache
        for item in blacklist:#Loop da Blacklist
            flag = string.find(item,site)
            if flag!=-1:
                print 'Acesso Negado (Blacklist)'
		insere_log(site, 'Encaminhamento Recusado(Blacklist)\n')
                mainsocket.send(str.encode('HTTP/1.1 200 OK\n Content-Type: text/html \n\n<html><head><title>Site Bloqueado</title></head><body><h1>ERROR 403 FORBIDDEN</h1><p>Site bloqueado pelo proxy!(Site Proibido)</p></body></html>\n'))
                break
        if flag!=-1:
            break
	flag=0#zera a flag pra ser usada pela Whitelist
        for item in whitelist:#loop da Whitelist
            flag = string.find(item, site)
            if flag != -1:
                print 'Acesso Permitido (Whitelist)'
                insere_log(site, 'Encaminhamento Autorizado(Whitelist)\n')
                for i in range(0,n_url): #verifica se tem na cache
                    if site==URL_cache[i]:
                        tem_cache=i
                if tem_cache!=0:
                    resposta_site = Dados_cache[tem_cache] #le direto da cache
                    print 'leu da cache'
                    mainsocket.send(resposta_site)
                    break
                else:
                    s_site = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    s_site.connect((socket.gethostbyname(site),80))
                    s_site.sendall(data) #faz a requisicao para os dados do site
                    while 1:
                        resposta_site = s_site.recv(4194304)#recebe os dados do site
                        if not resposta_site:
                            s_site.close()
                            break
                        URL_cache.insert(n_url,site) #insere o site na cache
                        print 'inseriu na cache %s' %(URL_cache[n_url])
                        Dados_cache.insert(n_url,resposta_site)
                        n_url+=1
                        mainsocket.send(resposta_site) #envia a resposta para o cliente
                    break
        if flag != -1:
            break
	flag=0#zera a flag para ser usada pelo DenyTerms
        for i in range(0,n_url):#verifica se esta na cache
            if site==URL_cache[i]:
                tem_cache=i
        if tem_cache!=0:
            resposta_site = Dados_cache[tem_cache]#le direto da cache
            print 'leu da cache'
        else:
            s_site = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s_site.connect((socket.gethostbyname(site),80))
            s_site.sendall(data)#faz a requisicao para os dados do site
        while 1:
            if tem_cache==0:
                resposta_site = s_site.recv(4194304)#recebe os dados do site
                if not resposta_site:
                    s_site.close()
                    break
                URL_cache.insert(n_url,site)#insere na cache
                print 'inseriu na cache %s' %(URL_cache[n_url])
                Dados_cache.insert(n_url,resposta_site)
                n_url+=1
            aux = resposta_site.split('\n')
            http = aux[0].split(' ')
            try:#verificacao dos Deny terms
                if(http[0].find('HTTP/1.1'))!=-1: #verificar se tem cabecalho
                    if int(http[1])>=200 and int(http[1])<300: #verificar se e um pacote de confirmacao
                        tipo = resposta_site.find('Content-Type: text/html')
                        if tipo!=-1:
                            print 'verificando deny terms'
                            for item in denyterms:
                                flag = string.find(resposta_site,item[len(item)-1:])#procura os deny terms
                                if flag!=-1:
                                    print 'Termo invalido encontrado'
				    insere_log(site, 'Encaminhamento Recusado(DenyTerms)\n')
                                    if tem_cache==0:
                                        s_site.close()
                                    break
                            if flag!=-1:#enviar mensagem de conteudo restrito para o cliente
                                mainsocket.send(str.encode('HTTP/1.1 200 OK\n Content-Type: text/html \n\n<html><head><title>Site Bloqueado</title></head><body><h1>ERROR 403 FORBIDDEN</h1><p>Site bloqueado pelo proxy!(Conteudo Restrito)</p></body></html>'))
                                mainsocket.close()
                                break
                            print 'Nao foram encontrados termos invalidos'
			    insere_log(site, 'Encaminhamento Autorizado\n')
                            mainsocket.send(resposta_site)#envia o site pro cliente
                        else:#caso nao seja texto envia direto
                            mainsocket.send(resposta_site)
                    else:#caso nao seja de confirmacao, envia direto
                        mainsocket.send(resposta_site)
                        break
                else:#caso nao tenha cabecalho, verificar os dados
                    print 'verificando terms deny'
                    for item in denyterms:
                        flag = string.find(resposta_site,item[len(item)-1:])#procura os deny terms
                        if flag!=-1:
                            if tem_cache==0:
                                s_site.close()
                            print 'Termo invalido encontrado'
			    insere_log(site, 'Encaminhamento Recusado(DenyTerms)\n')
                            break
                    if flag!=-1:#enviar mensagem de conteudo restrito para o cliente
                        mainsocket.send(str.encode('HTTP/1.1 200 OK\n Content-Type: text/html \n\n<html><head><title>Site Bloqueado</title></head><body><h1>ERROR 403 FORBIDDEN</h1><p>Site bloqueado pelo proxy!(Conteudo Restrito)</p></body></html>'))
                        mainsocket.close()
                        break
                    print 'Nao foram encontrados termos invalidos'
		    insere_log(site, 'Encaminhamento Autorizado\n')
                    mainsocket.send(resposta_site)#caso o site nao tenha termos proibidos encaminha pro cliente
                    if tem_cache!=0:
                        break
            except Exception as IndexError:
                pass
    print 'Thread Fechada'
    mainsocket.close()#fecha o socket
    
def novaconeccao():#funcao que cria as novas threads de conecao
    while 1:
        (mainsocket, cliente) = s.accept()#aceita conecao do cliente
        print 'Nova Coneccao'
        thread.start_new_thread(mainfunct,(mainsocket,))#cria nova thread

white_file = open('whitelist.txt','r')
black_file = open('blacklist.txt','r')
terms_file = open('denyterms.txt','r')
whitelist = white_file.readlines()#carrega a Whitelist do arquivo
blacklist = black_file.readlines()#carrega a Blacklist do arquivo
denyterms = terms_file.readlines()#carrega o Denyterns di arquivo
white_file.close()
black_file.close()
terms_file.close()
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)#cria o socket do servidor com o navegador
s.bind(('127.0.0.1',9093))#porta e ip do servidor
s.listen(5)
print 'servidor criado'

novaconeccao()
