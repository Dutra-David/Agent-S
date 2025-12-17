"""ADB Bridge - Comunicação com Android via ADB"""

import subprocess
import os
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

class ADBBridge:
    """Comunica com Android via Android Debug Bridge (ADB)"""
    
    def __init__(self, device_id=None):
        self.device_id = device_id
        self.check_adb()
        logger.info("ADB Bridge inicializado")
    
    def check_adb(self):
        """Verifica se ADB está instalado"""
        try:
            result = subprocess.run(['adb', 'version'], capture_output=True, timeout=5)
            if result.returncode != 0:
                raise Exception("ADB não encontrado")
            logger.info("ADB encontrado e funcionário")
        except Exception as e:
            logger.error(f"Erro ao verificar ADB: {e}")
            raise
    
    def get_devices(self):
        """Lista todos os dispositivos conectados"""
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = []
        for line in result.stdout.split('\n')[1:]:
            if 'device' in line and 'attached' not in line:
                device_id = line.split('\t')[0]
                devices.append(device_id)
        logger.info(f"Dispositivos encontrados: {devices}")
        return devices
    
    def get_screenshot(self):
        """Tira screenshot do Android"""
        try:
            subprocess.run(['adb', 'shell', 'screencap', '-p', '/sdcard/screenshot.png'], 
                          capture_output=True, timeout=10)
            subprocess.run(['adb', 'pull', '/sdcard/screenshot.png', 'temp_screenshot.png'],
                          capture_output=True, timeout=10)
            
            img = Image.open('temp_screenshot.png')
            buffered = io.BytesIO()
            img.save(buffered, format='PNG')
            logger.info("Screenshot capturado com sucesso")
            return buffered.getvalue()
        except Exception as e:
            logger.error(f"Erro ao capturar screenshot: {e}")
            raise
    
    def tap(self, x, y):
        """Toca em coordenadas (x, y)"""
        subprocess.run(['adb', 'shell', 'input', 'tap', str(x), str(y)], 
                      capture_output=True, timeout=5)
        logger.debug(f"Toque em ({x}, {y})")
    
    def type_text(self, text):
        """Digita texto"""
        escaped_text = text.replace('"', '\\"').replace('$', '\\$')
        subprocess.run(['adb', 'shell', 'input', 'text', escaped_text], 
                      capture_output=True, timeout=5)
        logger.debug(f"Texto digitado: {text}")
    
    def open_app(self, package_name):
        """Abre um app pelo package name"""
        subprocess.run(['adb', 'shell', 'am', 'start', '-n', f'{package_name}/.MainActivity'],
                      capture_output=True, timeout=5)
        logger.info(f"App aberto: {package_name}")
    
    def go_home(self):
        """Volta para tela inicial"""
        subprocess.run(['adb', 'shell', 'input', 'keyevent', '3'], capture_output=True)
        logger.debug("Voltado para home")
    
    def go_back(self):
        """Pressiona botão voltar"""
        subprocess.run(['adb', 'shell', 'input', 'keyevent', '4'], capture_output=True)
        logger.debug("Botão voltar pressionado")
    
    def list_apps(self):
        """Lista todos os apps instalados"""
        result = subprocess.run(['adb', 'shell', 'pm', 'list', 'packages'], 
                               capture_output=True, text=True)
        return [pkg.replace('package:', '') for pkg in result.stdout.split('\n') if pkg]
