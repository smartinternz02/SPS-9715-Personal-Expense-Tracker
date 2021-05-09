def monthgen(m,z):
    x=[]
    if(m<=12):
        if(m==2):
            if(z%4==0 & z%100==0 & z%400):
                for i in range(1,30):
                    if(i<=9 and m<10):
                        y = f'{z}-0{m}-0{i}'
                    elif(i<=9 and m >=10):
                        y = f'{z}-{m}-0{i}'
                    elif(i>=10 and m<10):
                        y = f'{z}-0{m}-{i}'
                    else:
                        y = f'{z}-{m}-{i}'
                    x.append(y)
            else:
                for i in range(1,29):
                    if(i<=9 and m<10):
                        y = f'{z}-0{m}-0{i}' 
                    elif(i<=9 and m >=10):
                        y = f'{z}-{m}-0{i}'
                    elif(i>=10 and m<10):
                        y = f'{z}-0{m}-{i}'
                    else:
                        y = f'{z}-{m}-{i}'
                    x.append(y)
        elif(m<=7):
            if(m%2==0):
                for i in range(1,31):
                    if(i<=9 and m<10):
                        y = f'{z}-0{m}-0{i}'
                    elif(i<=9 and m >=10):
                        y = f'{z}-{m}-0{i}'
                    elif(i>=10 and m<10): 
                        y = f'{z}-0{m}-{i}'
                    else:
                        y = f'{z}-{m}-{i}'
                    x.append(y)
            else:
                for i in range(1,32):
                    if(i<=9 and m<10):
                        y = f'{z}-0{m}-0{i}'
                    elif(i<=9 and m >=10):
                        y = f'{z}-{m}-0{i}'
                    elif(i>=10 and m<10):
                        y = f'{z}-0{m}-{i}'
                    else:
                        y = f'{z}-{m}-{i}'
                    x.append(y)
        else:
            if(m%2==0):
                for i in range(1,32):
                    if(i<=9 and m<10):
                        y = f'{z}-0{m}-0{i}'
                    elif(i<=9 and m >=10):
                        y = f'{z}-{m}-0{i}'
                    elif(i>=10 and m<10):
                        y = f'{z}-0{m}-{i}'
                    else:
                        y = f'{z}-{m}-{i}'
                    x.append(y)
            else:
                for i in range(1,31):
                    if(i<=9 and m<10):
                        y = f'{z}-0{m}-0{i}'
                    elif(i<=9 and m >=10):
                        y = f'{z}-{m}-0{i}'
                    elif(i>=10 and m<10):
                        y = f'{z}-0{m}-{i}'
                    else:
                        y = f'{z}-{m}-{i}'
                    x.append(y)
    return x
