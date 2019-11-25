import requests

enable_log = True

def log(obj, err=False):
    if enable_log:
        ext = ''
        if err:
            ext = '.error'
        file = open('hartic' + ext + '.log', 'a')

        from time import localtime, strftime
        date = strftime("%d-%m-%Y %H:%M:%S", localtime())
        file.write('--------- ' + date + ' ---------\n')
        if type(obj) == requests.models.Response:
            req = obj.request
            file.write('REQUEST:\n')
            file.write(req.method + ' ' + req.url + '\n')
            for h in req.headers.keys():
                file.write(h + ': ' + req.headers[h] + '\n')
            if req.body:
                file.write('\n' + str(req.body) + '\n')
            file.write('\nRESPONSE:\n')
            file.write(str(obj.status_code) + '\n')
            for h in obj.headers.keys():
                file.write(h + ': ' + obj.headers[h] + '\n')
            if obj.text:
                file.write('\n' + str(obj.text) + '\n')
        else:
            file.write(str(obj) + '\n')
        file.write('\n\n')
        file.close()

def error(obj):
    return log(obj, True)
