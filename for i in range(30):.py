for i in range(30):
        try:
            col_name = f'calificacion{i}'
            scores = []
            nucleos = []
            for row in df[col_name]:
                if row:
                    for item in row:
                        if f'score{i}' in item:
                            scores.append(item[f'score{i}'])
                        if f'nucleo{i}' in item:
                            nucleos.append(item[f'nucleo{i}'])
            if len(scores) == len(result.index):
                try:
                    result[f'score{i}'] = scores
                except ValueError:
                    print("Length of scores exceeds length of index")
                    pass
            elif len(scores) < len(result.index):
                try:
                    scores += [None] * (len(result.index) - len(scores))
                    result[f'score{i}'] = scores
                except ValueError:
                    print("Length of scores exceeds length of index")
                    pass
            else:
                raise ValueError("Length of scores exceeds length of index")
            
            if len(nucleos) == len(result.index):
                try:
                    result[f'nucleo{i}'] = nucleos
                except ValueError:
                    print("Length of nucleos exceeds length of index")
                    pass
            elif len(nucleos) < len(result.index):
                try:
                    nucleos += [None] * (len(result.index) - len(nucleos))
                    result[f'nucleo{i}'] = nucleos
                except ValueError:
                    print("Length of nucleos exceeds length of index")
                    pass
            else:
                raise ValueError("Length of nucleos exceeds length of index")
        except:
            pass