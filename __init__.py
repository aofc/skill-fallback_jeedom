from neon_utils.skills.neon_fallback_skill import NeonFallbackSkill
from ovos_workshop.decorators import intent_handler, resting_screen_handler
from mycroft.configuration import LocalConf, USER_CONFIG
import requests
import re
import subprocess
import time
from ovos_bus_client import Message
from ovos_utils import classproperty

class JeedomFallback(NeonFallbackSkill):
    """
        Compétence permettant d'interagir avec un Jeedom par commandes vocales en fallback.
    """
    def __init__(self):
        super(JeedomFallback, self).__init__(name='Fallback Jeedom')
        # Add your own initialization code here


    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(internet_before_load=False,
                                   network_before_load=True,
                                   gui_before_load=True,
                                   requires_internet=False,
                                   requires_network=True,
                                   requires_gui=True,
                                   no_internet_fallback=True,
                                   no_network_fallback=False,
                                   no_gui_fallback=False)

    @resting_screen_handler('JeedomHomescreen')
    def handle_idle(self, message):
        self.persistent_menu_hint = self.settings.get("persistent_menu_hint", False)
        self.gui["persistent_menu_hint"] = self.persistent_menu_hint

        url = self.settings.get('homepage_url')
        if re.search(r"key\=$", url):
            url += self.settings.get('api_key')
        self.gui.clear()
        self.log.info('Activating JeedomHomescreen')
        if url != "":
            self.gui.show_url(url, override_idle=True, override_animations=False)

    def initialize(self):
        """
            Registers the fallback handler and idle screen
        """
        self.register_fallback(self.handle_fallback, 3)
        #self.bus.emit(Message("mycroft.device.show.idle"))
        self.handle_idle(Message("mycroft.device.show.idle"))

    def handle_fallback(self, message):
        api_key = self.settings.get('api_key')
        url = self.settings.get('url')
        verif = self.settings.get('verify')
        room = self.settings.get('room')

        if not(api_key) or url == "http://my.jeedom.url" or not(url):
            self.speak(utterance="Vous devez configurer la clé d'API et l'adresse URL de votre Jeedom avant de pouvoir lui parler.", speaker={'language': 'fr-ca', 'gender': 'male', 'name':''})
            return False

        utterance = format(message.data.get('utterance'))
        if utterance:
            if re.search(r'((mets|mettre|mise) (à|a) jour|update) (de |le |)(neon|néon)', utterance, re.IGNORECASE):
                self.speak(utterance="Je mets à jour Néon.", speaker={'language': 'fr-ca', 'gender': 'male', 'name': ''})
                time.sleep(7)
                sp = subprocess.call(['sh', '/home/neon/.local/share/neon/skills/skill-fallback_jeedom.aofc/neon_updater.sh'])
                return True if not sp else False
            else:
                r = requests.get(url+"/core/api/jeeApi.php?apikey="+api_key+"&type=interact&profile="+room+"&query="+utterance, verify=verif)
                response = re.sub(r'^\w*(.*)\w*$', r'\1', r.text)
                if response != "":
                    self.speak(utterance=response, speaker={'language': 'fr-ca', 'gender': 'male', 'name': ''})
                    return True
                else:
                    return False
        else:
            return False

    def on_network_connected(self, message):
        self.system_connectivity = "network"
        self.gui["system_connectivity"] = self.system_connectivity

    def on_internet_connected(self, message):
        self.system_connectivity = "online"
        self.gui["system_connectivity"] = self.system_connectivity

    def on_no_internet(self, message):
        self.system_connectivity = "offline"
        self.gui["system_connectivity"] = self.system_connectivity

    def shutdown(self):
        """
            Remove this skill from list of fallback skills.
        """
        self.remove_fallback(self.handle_fallback)
        super(JeedomFallback, self).shutdown()

def create_skill():
    return JeedomFallback()
