from sys import argv

from movslib.buoni import read_buoni


def main()->None:
    for fn in argv[1:]:
        _, csv = read_buoni(fn)
        for row in csv:
            print(f'{row.data_contabile:%m/%d/%Y},'
                  f'{row.data_valuta:%m/%d/%Y},'
                  f'{row.addebiti},'
                  f'{row.accrediti},'
                  f'{row.descrizione_operazioni}')
if __name__=='__main__':
    main()
