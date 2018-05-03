"""
SUNA output settings for this are set to 'CONCENTRATION' so the spectra outputs are suppressed and ignored.
Dark count is bypassed and not included in the averaging. But a Dark count should be taken prior to light count.. helps adjusting for temperature.

Jason Adelaars

"""

import numpy as np
import serial
import time

def getSUNA(suna,nsample):
    '''
    Obtain nitrate measurement from SUNA sensor operating in polled mode.
    
    This version has been tested on Python 3 only.
    
    INPUTS:
    suna - a Serial object
    nsample - number of light samples to average
    
    RETURNS
    nitrate_uM (umol/L)
    nitrogen (mg/L)
    '''
    
    try:
        print('Connected to SUNA'+'\n')
        
        suna.write(b'Waking up SUNA\n')
        wake1 = suna.readline().decode()
        print('wake1: ' + wake1+'\n')
        wake2 = suna.readline().decode()
        print('wake2: ' + wake2+'\n')
        print('Woken up SUNA, exit from command line'+'\n')
        suna.write(b'exit\n')
        
        #wait a few secs
        time.sleep(10)
        
        #SATSDF: SUNA Dark Full: blank dark reading
        #SATSLF: this has the data in it. Check SUNA hardware manual pg 58 for column headers
        #... full ascii column
        
        #Request data, take samples and average them together
        sample_command = 'measure '+str(nsample)+'\n'
        try:
            suna.write(sample_command)
        except:
            suna.write(str.encode(sample_command))
            
        nitrate_list=[]
        nitrogen_list = []
        
        count = 1
        # Loop through until done, limit to nsample*10 to avoid infinite loop
        for i in range(nsample*10):
            try:
                line=suna.readline().decode()
            except:
                line=suna.readline()
            print('Line: '+line+'\n')
            if 'SATSL' in line:
                #Only average the light counts
                data = line.split(',')
                nitrate_list.append(float(data[3]))
                nitrogen_list.append(float(data[4]))
                count = count+1
            if count > nsample:
                break
        
        suna.close()
        
        
        
        data = line.split(',')
        nitrate_uM = np.mean(nitrate_list)
        nitrogen = np.mean(nitrogen_list)
        
        print ('*****************************************\n')
        print ('Nitrate (uM): '+str(nitrate_uM)+'\n')
        print ('Nitrogen (mg/L): '+str(nitrogen)+'\n')
        print ('*****************************************\n')
        
        
        return (nitrate_uM, nitrogen)

    
    except:
        
        print ('No data received from SUNA.'+'\n')
        return ('NA','NA')
    
if __name__ == '__main__':

    COM_SUNA = 'COM4'  # COM port
    nsample = 10       # number of light frames averaged together
    sensor = serial.Serial(COM_SUNA,57600,timeout=10)
    nitrate_uM,nitrogen = getSUNA(sensor,nsample)
    sensor.close()
