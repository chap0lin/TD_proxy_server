import socket
import thread
import string
import binascii

URL_cache = []
Dados_cache = []
n_url=0

def mainfunct(mainsocket):
    while 1:
        global n_url
        global URL_cache
        global Dados_cache
        data = mainsocket.recv(2048)
        if not data: break
        aux = data.split('\n')
        site = (aux[1].split())[1]
        print site
        ebl=0
        ewl=0
        edt=0
        tem_cache=0
        for item in blacklist:
            ebl = string.find(item,site)
            if ebl!=-1:
                print 'Acesso Negado'
                mainsocket.send(str.encode('HTTP/1.1 200 OK\n Content-Type: text/html \n\n<html><head><title>Site Bloqueado</title></head><body><h1>ERROR 403 FORBIDDEN</h1><p>Site bloqueado pelo proxy!(Site Proibido)</p></body></html>\n'))
                break
        if ebl!=-1:
            break
        for item in whitelist:
            ewl = string.find(item, site)
            if ewl != -1:
                print 'Acesso Permitido'
                
                for i in range(0,n_url):
                    if site==URL_cache[i]:
                        tem_cache=i
                if tem_cache!=0:
                    resposta_site = Dados_cache[tem_cache]
                    print 'leu da cache'
                    mainsocket.send(resposta_site)
                    break
                else:
                    s_site = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    s_site.connect((socket.gethostbyname(site),80))
                    s_site.sendall(data)
                    while 1:
                        resposta_site = s_site.recv(4194304)
                        if not resposta_site:
                            s_site.close()
                            break
                        URL_cache.insert(n_url,site)
                        print 'inseriu na cache %s' %(URL_cache[n_url])
                        Dados_cache.insert(n_url,resposta_site)
                        n_url+=1
                        mainsocket.send(resposta_site)
                    break
        if ewl != -1:
            break
        for i in range(0,n_url):
            if site==URL_cache[i]:
                tem_cache=i
        if tem_cache!=0:
            resposta_site = Dados_cache[tem_cache]
            print 'leu da cache'
        else:
            s_site = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s_site.connect((socket.gethostbyname(site),80))
            s_site.sendall(data)
        while 1:
            if tem_cache==0:
                resposta_site = s_site.recv(4194304)
                if not resposta_site:
                    s_site.close()
                    break
                URL_cache.insert(n_url,site)
                print 'inseriu na cache %s' %(URL_cache[n_url])
                Dados_cache.insert(n_url,resposta_site)
                n_url+=1
            aux = resposta_site.split('\n')
            http = aux[0].split(' ')
            try:
                if(http[0].find('HTTP/1.1'))!=-1:
                    if int(http[1])>=200 and int(http[1])<300:
                        tipo = resposta_site.find('Content-Type: text/html')
                        if tipo!=-1:
                            print 'verificando deny terms'
                            for item in denyterms:
                                edt = string.find(resposta_site,item[len(item)-1:])
                                if edt!=-1:
                                    print 'Wasted'
                                    if tem_cache==0:
                                        s_site.close()
                                    break
                            if edt!=-1:
                                mainsocket.send(str.encode('HTTP/1.1 200 OK\n Content-Type: text/html \n\n<html><head><title>Site Bloqueado</title></head><body><h1>ERROR 403 FORBIDDEN</h1><p>Site bloqueado pelo proxy!(Conteudo Restrito)</p></body></html>'))
                                mainsocket.close()
                                break
                            print 'not Wasted'
                            mainsocket.send(resposta_site)
                        else:
                            mainsocket.send(resposta_site)
                    else:
                        mainsocket.send(resposta_site)
                        break
                else:
                    print 'verificando terms deny'
                    for item in denyterms:
                        edt = string.find(resposta_site,item[len(item)-1:])
                        if edt!=-1:
                            if tem_cache==0:
                                s_site.close()
                            print 'Wasted dude'
                            break
                    if edt!=-1:
                        mainsocket.send(str.encode('HTTP/1.1 200 OK\n Content-Type: text/html \n\n<html><head><title>Site Bloqueado</title></head><body><h1>ERROR 403 FORBIDDEN</h1><p>Site bloqueado pelo proxy!(Conteudo Restrito)</p></body></html>'))
                        mainsocket.close()
                        break
                    print 'not Wasted dude'
                    mainsocket.send(resposta_site)
                    if tem_cache!=0:
                        break
            except Exception as IndexError:
                pass
    print 'uhuu'
    mainsocket.close()
    
def novaconeccao():
    while 1:
        (mainsocket, cliente) = s.accept()
        print 'conecao estabelecida'
        thread.start_new_thread(mainfunct,(mainsocket,))

white_file = open('whitelist.txt','r')
black_file = open('blacklist.txt','r')
terms_file = open('denyterms.txt','r')
whitelist = white_file.readlines()
blacklist = black_file.readlines()
denyterms = terms_file.readlines()
white_file.close()
black_file.close()
terms_file.close()
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('127.0.0.1',9092))
s.listen(5)
print 'servidor criado'

novaconeccao()
