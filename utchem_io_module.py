
import pandas as pd
import numpy as np


def import_hist(filepath: str, sr: int = 0) -> pd.DataFrame:

    tv = -1
    real_headers = []
    phase_cuts = False
    p_tot = 3

    with open(filepath, 'r') as file:
        line = 'test'
        while line is not None and tv == -1:
            line = file.readline()
            if line.find('1-PV') != -1:
                real_headers = line.split(',')
            elif line.find('TOTAL NO. OF VARIABLES FOR A ') == 3:
                try:
                    tv = int(line.split()[-1])
                except ValueError:
                    tv = -1
                    line = None
            elif real_headers:

                stuff = line.split(':')
                nums = stuff[0].split('-')
                num1 = int(nums[0].strip())
                num2 = int(nums[1].strip())
                num_tot = num2 - num1 + 1

                if not phase_cuts:
                    real_headers.append('--water cut')
                    real_headers.append('--oil cut')
                    real_headers.append('--m.e. cut')
                    if num_tot == 4:
                        real_headers.append('--gas cut')
                        p_tot = 4
                    phase_cuts = True

                elif num_tot == 1:
                    real_headers.append('--' + stuff[1].strip())

                elif stuff[1].find('PHASE') != -1:
                    component = stuff[1].split()[-1].strip()
                    real_headers.append('--{} in water'.format(component))
                    real_headers.append('--{} in oil'.format(component))
                    real_headers.append('--{} in m.e.'.format(component))
                    if p_tot == 4:
                        real_headers.append('--{} in gas'.format(component))
                    real_headers.append('--total {}'.format(component))

                else:
                    real_headers.append('--CSEL')
                    real_headers.append('--CSEU')
                    real_headers.append('--CSE')

    df = pd.read_csv(filepath, skiprows=sr)
    new_data = np.array(np.zeros((df.values.shape[0] + 1, df.values.shape[1])))
    for i, h in enumerate(df.columns):
        try:
            new_data[0, i] = float(h)
        except ValueError:
            new_data[0, i] = np.nan
    new_data[1:, :] = df.values[:, :]
    data_rows = 0
    data_count = 0
    while data_count < tv:
        d_row = new_data[data_rows, :]
        non_nan = np.where(~np.isnan(d_row))
        data_count += np.size(d_row[non_nan])
        data_rows += 1

    s = new_data.shape
    new_data = new_data.reshape((int(s[0] / data_rows), s[1] * data_rows))
    s = new_data.shape
    first_row = new_data[0, :]
    non_nan = np.where(~np.isnan(first_row))
    final_data = np.zeros((s[0], np.size(first_row[non_nan])))
    k = 0
    for j in range(s[1]):
        if ~np.isnan(first_row[j]):
            final_data[:, k] = new_data[:, j]
            k += 1

    names = []
    for i in range(tv):
        if i < len(real_headers):
            names.append(real_headers[i].strip()[2:].lstrip())
            continue
        names.append('{}'.format(i + 1))

    return pd.DataFrame(data=final_data, columns=names)


def main():
    import time
    from matplotlib import pyplot as plt

    start_time = time.time()

    df = import_hist('C:\\Users\\jdriver\\Desktop\\02 Coreflood\\CORESP.HIST02', 23)

    plt.plot(df.values[:, 0], df.values[:, 7], 'r-')
    plt.xlabel(df.columns[0])
    plt.ylabel(df.columns[7])

    print('{:.5f} seconds'.format(time.time() - start_time))

    plt.show()


if __name__ == '__main__':
    main()
