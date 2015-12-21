#!/usr/bin/env bash

#run this in src
pyinstaller --onefile web2board.spec



#deb creator
dpkg-deb --build web2board_0.5



[Desktop Entry]
Encoding=UTF-8
Comment=Install
Exec=bash -c 'echo $ "-------------------------------------------------- " && echo  "  INSTALANDO WEB2BOARD PARA BITBLOQ. NO CERRAR " && echo  "  INSTALLING BITBLOQS WEB2BOARD. DO NOT CLOSE" && echo $ "--------------------------------------------------\n\n\n " && echo  "Instalando... " && echo  "Installing... " && userName=$( who | head -1| cut -d  " " -f 1) && sudo adduser $userName dialout && sudo apt-get -y install gdebi && sudo apt-get install xterm && sudo apt-get install wget && wget http://bitbloq.com.s3.amazonaws.com/dev/qa/linux/64bit/web2board.deb && sudo gdebi --non-interactive web2board.deb && rm web2board.deb && echo $ "\n\n\n-------------------------------------------------- " && echo  "INSTALACIÓN TERMINADA. PUEDE CERRAR LA VENTANA " && echo  "INSTALLATION FINISHED. YOU MAY CLOSE THE WINDOW " && echo  "REINICIE EL ORDENADOR " && echo  "REBOOT THE COMPUTER " && echo $ "--------------------------------------------------\n\n\n " && sudo chown -R $userName ~/Arduino'
Terminal=true
Type=Application
