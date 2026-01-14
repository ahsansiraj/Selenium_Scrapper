import re
from selenium.webdriver.common.by import By

# ---------- MATCHING CONFIGURATION ----------
STOP_WORDS = {'version', 'international', 'gb', 
              'single', 'sim', 'unlocked', 'Pre-Owned Phone', 'Pre-Owned Smart Phone' ,
               'Plus', 'renewed', 'refurbished', '+', 'esim', 'wifi', 'cellular',
              'physical', 'dual'}

PENALTY_WORDS = {'case', 'cover', 'protector','protector case cover', 'accessory', 'skin', 'sticker', 
                 'film', 'adapter', 'charger', 'cable', 'stand', 'holder', 
                 'mount', 'grip', 'ring', 'glass', 'shield', 'sleeve', 'pouch', 
                 'bag', 'box', 'holster', 'battery', 'dock', 'keyboard','Protective Case Cover'}

BRANDS = {
    # Phones, Laptops, Tablets, Accessories, Audio, Gaming, Networking, etc.
    '3m', 'aee', 'activision', 'acer', 'anker', 'apple', 'ashdown', 'astro', 'atlas', 'atgames', 'atouch', 'aruba',
    'asus', 'avita', 'beelink', 'beats', 'bend studio', 'blackberry', 'bose', 'brother', 'bsnl', 'c idea', 'canon',
    'cat', 'cooler master', 'condor', 'corsair', 'cougar', 'cronus', 'ctroniq', 'd-link', 'dell', 'discover', 'dji',
    'dobe', 'ea sports', 'edifier', 'elgato', 'energizer', 'energy sistem', 'enet', 'epson', 'epic games', 'evvoli',
    'ezzyso', 'fotga', 'four', 'fujitsu', 'gameon', 'gamesir', 'genius', 'generic', 'gioteck', 'gizmore', 'godox',
    'goui', 'google', 'gqui', 'harman kardon', 'havit', 'hezire', 'hikvision', 'honeywell', 'honor', 'hope', 'hp',
    'htc', 'hxsj', 'hyper x', 'i-life', 'ibrand', 'iconix', 'ignited 7pro', 'infinix', 'innjoo', 'intex', 'isonic',
    'jbl', 'joyroom', 'jabra', 'kano', 'kingone', 'kotion each', 'lava', 'lenovo', 'lg', 'linksys', 'limeide',
    'logitech', 'm-audio', 'marshall', 'meizu', 'meta', 'microsoft', 'mione', 'monster', 'motorola', 'mpow', 'msi',
    'mycandy', 'nacon', 'nintendo', 'nokia', 'nothing', 'nova', 'nubia', 'nvidea', 'nubwo', 'occuwzz', 'onikuma',
    'onn', 'oneplus', 'papada', 'panasonic', 'pebble', 'philips', 'piranha', 'poco', 'powera', 'prime', 'promate',
    'pxn', 'rapoo', 'razer', 'realme', 'redragon', 'redmi', 'rii', 'roccat', 'rock candy', 'rockstar games',
    's-color', 'sades', 'sanno', 'samsung', 'sega', 'sennheiser', 'sharp', 'skullcandy', 'sonos', 'sony',
    'soundpeats', 'steelseries', 'stuffcool', 'subsonic', 'suunto', 'sup', 'super general', 'suzuki', 'targus',
    'techno', 'teso', 'thrustmaster', 'tile', 'tokina', 'toshiba', 'tp-link', 'trands', "t'nb", 'turtle beach',
    'ubiquiti', 'ugreen', 'vestel', 'veger', 'venom', 'v380', 'vivo', 'wiko', 'wolverine', 'wopow', 'xbox',
    'xiaomi', 'xtrike', 'xtrike me', 'xerox', 'zakk', 'zendure', 'zebra', 'zealot', 'zte',
    # Existing/legacy/edge cases
    'msi', 'dell', 'hp', 'lenovo', 'lg', 'asus', 'acer', 'huawei', 'nova', 'oppo', 'vivo', 'realme', 'oneplus',
    'honor', 'redmi', 'poco', 'motorola', 'nokia', 'sony', 'google', 'pre-owned phone', 'pre-owned smart phone',
    # Duplicates with different casing for robustness
    'apple', 'dell', 'asus', 'msi', 'samsung', 'sony', 'microsoft', 'xiaomi', 'lenovo', 'oneplus', 'realme', 'vivo',
    'honor', 'redmi', 'poco', 'cat', 'blackberry', 'htc', 'meizu', 'infinix', 'itel', 'jio', 'karbonn', 'lava',
    'leeco', 'micromax', 'cubot', 'energizer', 'fairphone', 'gigaset', 'bosch', 'alcatel', 'amazon', 'aqu',
    'all call',
}

MODEL_KEYWORDS = {

    'Pre-Owned Phone', 'Pre-Owned Smart Phone',
    # Added model names from the provided list:
    'iPhone 11', 'Rio S', '1C 2019', '1T7', 'iPhone 11 Pro', 'iPhone 11 Pro Max', 'iPhone 12', 'iPhone 12 Pro',
    'iPhone 14 Pro', 'iPhone 14 Pro Max', 'iPhone 15', 'iPhone 15 Plus', 'iPhone 15 Pro', 'iPhone 15 Pro Max',
    'iPhone 16 Pro Max', 'iPhone 4S', 'iPhone 5', 'iPhone 5S', 'iPhone 6', 'iPhone 6 Plus', 'iPhone 6S',
    'iPhone 6S Plus', 'iPhone 7', 'iPhone 7 Plus', 'iPhone 8', 'iPhone 8 Plus', 'iPhone SE 2020', 'iPhone SE 2022',
    'iPhone SE 2016', 'iPhone X', 'iPhone XR', 'iPhone XS', 'iPhone XS Max', 'Aquos 605SH', 'Aquos 701SH',
    'Rog Phone 2', 'Rog Phone 3', 'Rog Phone 5', 'ROG Phone', 'ZenFone Max', 'ZenFone Max Plus', 'Bold 9790',
    'Curve 9320', 'Leap', 'Porsche Design', 'Q10', 'Torch 9800', 'S60', 'Griffe T1', 'Joy 3 B104', 'Raku-Raku',
    'Pixel 2 XL', 'Play', 'X7B', 'X8A', 'X9A', 'F88', 'S15', 'S17', 'Desire 10', 'Desire 12 Plus', 'Desire 310',
    'Desire 520', 'Desire 526', 'Desire 530', 'Desire 828', 'Desire 830', 'M8 Eye', 'One M9', 'U Play', 'U20',
    'Wildfire E Plus', 'Wildfire E3 Lite', 'Ascend P7', 'GR5 2017', 'Honor 9 Lite', 'Mate 10 Lite', 'Mate 20 Lite',
    'Mate 20 Pro', 'Mate 30 Pro', 'Mate 40 Pro', 'Mate 50', 'Mate20 Pro', 'Mate20 X', 'Nova 2', 'Nova 3i',
    'Nova 5T', 'Nova 7', 'Nova 7i', 'Nova 8I', 'Nova Y61i', 'Nova Y70', 'P Smart', 'P Smart Plus', 'P10 Lite',
    'P20', 'P20 Lite', 'P20 Pro', 'P30 Lite', 'P30 Pro', 'P40 Lite', 'P50 Pocket', 'P50 PRO', 'P8', 'P8 Lite 2017',
    'P8 Lite 2018', 'Y5 2019', 'Y5 Lite', 'Y5 Prime 2018', 'Y5 Prime 2019', 'Y5P', 'Y6 Prime 2018', 'Y6 Pro 2017',
    'Y6 Pro', 'Y6P', 'Y6S', 'Y7 Prime 2018', 'Y7 Prime 2019', 'Y7A', 'Y7P', 'Y8P', 'Y9 (2019)', 'Y9 2018',
    'Y9 2019', 'Y9 Prime 2019', 'Y9A', 'Y9S', 'Mate Xs 2', 'Nova 10 SE', 'Nova 3e', 'Y6 2019', 'Y6 Prime 2019',
    'A6 Note', 'A6000', 'A8', 'K10 Note', 'K4 Note', 'K5 Pro', 'K8 Note', 'K9 Note', 'Legion Pro', 'S920', 'Z5s',
    'G3', 'G4', 'G6', 'K220 (K10 2016)', 'Optimus One', 'V10', 'V20', 'Lumia 550', 'Lumia 640 XL', 'MI99',
    'Moto E40', 'Moto E7', 'Moto E7i', 'Moto Edge 30', 'Moto Edge 30 Ultra', 'Moto Edge 40', 'Moto Edge 50 Pro',
    'Moto Edge+', 'Moto G', 'Moto G Plus', 'Moto G13', 'Moto G22', 'Moto G23', 'Moto G24', 'Moto G30', 'Moto G31',
    'Moto G50', 'Moto G51', 'Moto G60S', 'Moto G62', 'Moto G73', 'Moto G82', 'Moto G84', 'Moto Razr 40',
    'Moto Razr 40 Ultra', 'Moto Razr', 'Moto Razr D1', 'C1 1', 'C2', 'C21', 'C21 Plus', 'C7-00', 'ES-00', 'G11',
    'G21', 'G50', 'N00', 'N6700', 'N9', 'N95', 'One X', 'X10', 'X6', 'F8B', 'J1', 'Red Magic 3', 'Red Magic 6',
    'Red Magic 6 Pro', 'Red Magic 8S Pro', '10 Pro', '10T', '11R', '5T', '6T', '7 Pro', '7T', '7T Pro Mclaren Edition',
    '8 Pro', '8T', '9 Pro', 'Nord', 'Nord 2', 'Nord CE', 'Nord N100', 'A15s', 'A16', 'A31', 'A37', 'A54', 'A55',
    'A57', 'A58', 'A5s', 'A60', 'A7', 'A77s', 'A78', 'A83', 'A9 2020', 'A93', 'A94', 'F15', 'F1s', 'F5', 'F7',
    'F9 Pro', 'R15X', 'Reno 10', 'Reno 11', 'Reno 2', 'Reno 3', 'Reno 4', 'Reno 5', 'Reno 7', 'Reno', 'Reno 8T',
    'F185', 'Link X6', 'P1', 'Prime 09', 'C11', 'C17', 'C25Y', 'C3', 'C53', 'GT 2 Pro', 'GT Master', 'X50',
    'Redmi K20', 'Redmi Note 8', 'Redmi Note 9', 'Redmi Note 9 Pro', 'A9 PRO', 'C160M', 'Corby GT-S3653W',
    'Galaxy A01', 'Galaxy A01 Core', 'Galaxy A02', 'Galaxy A02s', 'Galaxy A03', 'Galaxy A03 Core', 'Galaxy A03s',
    'Galaxy A05', 'Galaxy A10', 'Galaxy A10s', 'Galaxy A11', 'Galaxy A12', 'Galaxy A13', 'Galaxy A14', 'Galaxy A15',
    'Galaxy A20', 'Galaxy A20s', 'Galaxy A21S', 'Galaxy A22', 'Galaxy A25', 'Galaxy A30', 'Galaxy A30s', 'Galaxy A31',
    'Galaxy A32', 'Galaxy A33', 'Galaxy A34', 'Galaxy A40', 'Galaxy A42', 'Galaxy A5 2017', 'Galaxy A50',
    'Galaxy A50s', 'Galaxy A51', 'Galaxy A52', 'Galaxy A52s', 'Galaxy A53', 'Galaxy A54', 'Galaxy A6', 'Galaxy A60',
    'Galaxy A7 2016', 'Galaxy A7 2018', 'Galaxy A70', 'Galaxy A71', 'Galaxy A72', 'Galaxy A73', 'Galaxy A80',
    'Galaxy A90', 'Galaxy Alpha', 'Galaxy C8', 'Galaxy F13', 'Galaxy F42', 'Galaxy Fold', 'Galaxy Galaxy Grand Prime',
    'Galaxy Grand 2', 'Galaxy Grand Mega', 'Galaxy Grand Prime', 'Galaxy Grand Prime+', 'Galaxy J2 Prime',
    'Galaxy J3 (2016)', 'Galaxy J3 2016', 'Galaxy J5', 'Galaxy J6', 'Galaxy J6+', 'Galaxy J7 2016', 'Galaxy J7 Core',
    'Galaxy J7 Max', 'Galaxy J7 Prime', 'Galaxy J7 Pro 2017', 'Galaxy M10', 'Galaxy M11', 'Galaxy M12', 'Galaxy M14',
    'Galaxy M20', 'Galaxy M21', 'Galaxy M30', 'Galaxy M30s', 'Galaxy M31', 'Galaxy M31s', 'Galaxy M33', 'Galaxy M51',
    'Galaxy M52', 'Galaxy M53', 'Galaxy M62', 'Galaxy Mini 3', 'Galaxy Note 10', 'Galaxy Note 10 Lite',
    'Galaxy Note 10+', 'Galaxy Note 2', 'Galaxy Note 20', 'Galaxy Note 20 Ultra', 'Galaxy Note 3', 'Galaxy Note 4',
    'Galaxy Note 5', 'Galaxy Note 8', 'Galaxy Note 9', 'Galaxy Note Edge', 'Galaxy Note1', 'Galaxy Note20',
    'Galaxy Note20 Ultra', 'Galaxy ON 5', 'Galaxy ON 7', 'Galaxy ON7', 'Galaxy S10', 'Galaxy S10 Lite', 'Galaxy S10+',
    'Galaxy S10e', 'Galaxy S20', 'Galaxy S20 FE', 'Galaxy S20 Ultra', 'Galaxy S20+', 'Galaxy S21', 'Galaxy S21 FE',
    'Galaxy S21 Plus', 'Galaxy S21 Ultra', 'Galaxy S21+', 'Galaxy S21Plus 5', 'Galaxy S22', 'Galaxy S22 Ultra',
    'Galaxy S22+', 'Galaxy S23', 'Galaxy S23 FE', 'Galaxy S23 Plus', 'Galaxy S23 Ultra', 'Galaxy S23+', 'Galaxy S24',
    'Galaxy S24 Ultra', 'Galaxy S24+', 'Galaxy S3', 'Galaxy S5', 'Galaxy S6 Edge', 'Galaxy S6 Edge+', 'Galaxy S7',
    'Galaxy S7 Edge', 'Galaxy S8', 'Galaxy S8+', 'Galaxy S9', 'Galaxy S9 Plus', 'Galaxy S9+', 'Galaxy XCover 4s',
    'Galaxy Z Flip 3', 'Galaxy Z Flip 4', 'Galaxy Z Flip 5', 'Galaxy Z Flip', 'Galaxy Z Fold 2', 'Galaxy Z Fold 3',
    'Galaxy Z Fold 4', 'Galaxy Z Fold 5', 'Galaxy Z Fold 6', 'Grand 2', 'GT-I9100 (Galaxy S II)', 'J7 Prime', 'M12',
    'XCover Pro', 'IPX', 'Aquos SHV42', 'S1', 'R', 'T', 'Xperia 1 Mark 3', 'Xperia Arc S', 'Xperia C3',
    'Xperia C4 Dual', 'Xperia E3', 'Xperia E3 Dual', 'Xperia F3111', 'Xperia J', 'Xperia L', 'Xperia L3',
    'Xperia M2', 'Xperia S', 'Xperia SP', 'Xperia T2', 'Xperia T2 Ultra', 'Xperia T3', 'Xperia TX', 'Xperia V',
    'Xperia XA', 'Xperia XA1', 'Xperia XA1 Plus', 'Xperia XA1 Ultra', 'Xperia XZ', 'Xperia XZ1', 'Xperia Z',
    'Xperia Z1', 'Xperia Z1 Compact', 'Xperia Z3', 'Xperia Z3 Compact', 'Xperia Z5', 'Xperia ZR', 'Zperia Z3+',
    'Plex', 'Pova 5 Pro', 'IQOO Pro', 'V11 Pro', 'V21', 'V23', 'V29', 'V30', 'V30 Lite', 'X60', 'Y15', 'Y15s',
    'Y16', 'Y17', 'T3 W', 'Black Shark 2 Pro', 'Black Shark 3', 'Mi 10T', 'Mi 11 Lite', 'Mi 12T', 'Mi 9 SE',
    'Mi A3', 'Mi Note 10', 'Mi Note 10 Pro', 'Narzo 50A Prime', 'Note 10 Lite', 'Poco C3', 'Poco C65', 'Poco F2 Pro',
    'Poco F3', 'Poco F4', 'POCO F6', 'Poco M3', 'Poco M3 Pro', 'Poco M4 Pro', 'Poco M5', 'Redmi Note 10 Pro',
    'Redmi Note 10s', 'Redmi Note 11', 'Redmi Note 11 Pro+', 'Redmi Note 11S 8G', 'Redmi Note 11T 5G',
    'Redmi Note 12 Pro', 'Redmi Note 4', 'Redmi Note 5', 'Redmi Note 6 Pro', 'Redmi Note 7', 'Redmi Note 7 Pro',
    'Redmi Note 8 Pro', 'Redmi Note 9S', 'Redmi S2', '10 Lite', '7C', '8C', '8X', '10 EVO', '7 Plus', 'Phone 1',
    'Phone 2', '11 Pro', '5 Pro', '6 Pro', '6i', 'Redmi 10 Prime', 'Redmi 8', 'Redmi 9', 'Redmi 9 Power',
    'Redmi 9A', 'Redmi 9T Power', 'Mi 10', 'Mi 10T Pro', 'Mi 14 Ultra', 'Mi 5', 'Mi 9', 'Mi 9T', 'Mi 9T Pro',
    'Generic 113 Wireless Stereo Protable Speaker Black','2 Way Speaker Black','Bose 500','11 Lavalier','Anker Mono',
    'Sound Buds Rise','SoundBuds Curve','Soundbuds Lite','SoundBuds Mono','SoundBuds Rise','Soundbuds Surge','Soundbuds Verve',
    'Soundcore Arc','Soundcore Liberty 2','Soundcore Liberty Air 2','SoundCore Liberty Air','Soundcore Liberty Air X',
    'Soundcore Liberty Lite','Soundcore Liberty Neo','Soundcore Life 2 Neo',
    'Soundcore Life A2 NC','Soundcore Life Dot 2','Soundcore Life Note 3','Soundcore Life Note E',
    'Soundcore Life Note','Soundcore Life P2','Soundcore Life Q10','Soundcore Life Q20','SoundCore Life U2',
    'Soundcore mini','SoundCore Space NC','Soundcore Spirit 2','Soundcore Spirit Pro','SoundCore Spirit X',
    'Soundcore Strike 1','Soundcore Strike 3','AirPods 2nd Gen','AirPods 2nd Gen with Wireless Charging Case',
    'Airpods 3rd Gen','AirPods Max','AirPods Pro 2nd Gen','AirPods Pro','AirPods Pro with MagSafe Charging Case',
    'AirPods','AirPods with Wireless Charging Case','EarPods','Apple MNHF2','Arc Soundbar','OV-1-B-CONNECT',
    'Astro A10 Gen 2','Astro A10','Astro A10G01','Astro A20 Gen 2','Astro A40 TR','Astro A50 Gen4','Beats X',
    'Fit Pro','Beats Flex','Beats MLYE2LL/A','Beats Powerbeats3','Beats Urbeats 2nd Gen','Beats Wired EP',
    'Universal Stereo','BX5 D3','Bose Portable Home Speaker','Citation 700','D-203 Wired Stereo Speaker Black',
    'Darknets GS570','DAV-DZ650','Edifier X3','EM-3690FT','ESG 2','EVAUD-RB51A','Flip 6','Flip5',
    'General GM5 Wired In-Ear Headphones Red','General Wired In-Ear Headphones White','Generic Clear 1 Wireless In-Ear Headphones White',
    'Generic EarPods Wired In-Ear Headphones White','Generic Airpods Pro Wireless Noise Cancellation In-Ear Headphones White','Generic Airpods Wireless In-Ear Headphones White',
    'Generic Kids Wireless In-Ear Headphones Blue','Generic KZ ES4 Wired In-Ear Headphones Black','Generic Motorcycle Helmet Wireless In-Ear Headphones Black/Orange','Generic Oku one Side Wired In-Ear Headphones Black',
    'Generic PD-BE200 Wireless In-Ear Headphones Black','Generic SB Sound Audio controller Black','Generic Sound C13 Wired Over-Ear Headphones Brown','Generic Sports Wireless In-Ear Headphones Black',
    'Generic Sports Wireless In-Ear Headphones Blue','Generic Stereo Wireless In-Ear Headphones White','Generic UHF Dual Channel Microphone System Wireless Microphone Black',
    'Generic Wired Earphones Wired In-Ear Headphones Black','Generic Wired Gaming Headphones Black','Generic Wired In-Ear Headphones Black','Generic Wired Over-Ear Headphones Black',
    'Generic Wired Over-Ear Headphones Blue','Generic Wired Over-Ear Headphones Red','Generic Wireless In-Ear Headphones White',
    'Generic Wireless Noise Cancellation In-Ear Headphones White','Generic Wireless Over-Ear Headphones Black','Generic Wiwu V Wireless In-Ear Headphones Black',
    'Generic Y- Ear Wireless In-Ear Headphones Black','HS-M450','Gizmore Wired In-Ear Headphones Black','GL313AA','Go 2','Magnetic','Hezire Stereo Wired In-Ear Headphones White',
    'HomePod Mini','AM61','H100','HTC Wireless In-Ear Headphones Black','HTS40R','FreeBuds 3','FreeBuds 3i','FreeBuds 4i',
    'FreeBuds Lite','FreeBuds SE 2','FreeBuds SE','FreeBuds','Huawei Wired In-Ear Headphones White','FreeBuds 5i','Hunter Spider V2',
    'HWQ930BZN','Cloud Stinger 2','Cloud Stinger','iconix','iSonic 402','100-91400000-40','Elite 3','Elite 7','Evolve 20','Endurance Run',
    'Flex','JR460NC','Live 500','Live Pro+','QS-19','T110','T290','T450BT','Tune 110','Tune 120','Tune 125BT','Tune 205','Tune 205BT',
    'Tune 215','Tune 220','Tune 225','Tune 230NC','Tune 500','Tune 500BT','Tune 510BT','Tune 600BTNC','Tune 750BT','Wave Beam','Wave Buds','Wired Earbuds',
    'JR-T03 Pro','JR-T03S','Each G1000','Each G2000','Each G2100','Each G9000 Pro','Each GS700 Pro','Lenovo HE05','Livepods LP40 Pro',
    'LivePods LP40','Lenovo QT81','Lenovo LO1','Logitech G333','Logitech G435','Logitech G733','Logitech G935','4091743 Monitor','Mini Microphone Black',
    'Mini Wireless Stereo Protable Speaker Charcoal','Moto Buds 105','Moto Buds 250','Verve Buds 100','Verve Buds 110','Moxie V100','MP4/MP3 Protable Player','Music Box B2','TWS125','TWS300','Avviopro','Beat Master',
    'Beatpromax','Humming Buds','Hush M1','Mi Basic 2','Prodigy M2','Vive','Ear (1)','Ear (2)','N11','N7','Buds Pro 2','Bullets Wireless Z2','OnePlus Buds','K1-B','Wooden Bass Earphone','Spirit Neo','Zest Bassbuds','Boom','Power Beat','True Wireless Sports Stereo','Universal Mono','Promate Wireless In-Ear Headphones Black',
    'Pulse 3 Wireless Stereo Protable Speaker Black','Quran with Led Lamp Speaker White','Base Station V2 Chroma Headset Stand','Black Shark V2','Hammerhead','Karaken X Lite','Kraken','Kraken X','Redmi AirDots Youth','Elo X','S75Q Meridian','S8 Wireless Stereo Protable Speaker White','SA-810','SA-818','SA930','AKG','Dime 2','Galaxy Buds Live','Galaxy Buds','Galaxy Buds2','Gear IconX',
    'Level U','SM-R510NZAAXAR','USB- C Audio Adaptor','USB-C','SE6S','PXC 550','SK714','Dime 3','HD 450BT','Hesh Evo','Indy Evo','Jib XT','Jib+','Push','S2IQW-M448','Sesh Evo','Smokin\'','SNC4R','Sonic Boost 210','ICD-UX560F','MDR-EX155AP','MDR-ZX110','MDR-ZX110AP','WF-C500','WH-1000XM3','WH-1000XM4','WH-CH510','WH-CH520','WH-CH720N','WI-C200','WI-XB400','SoundCore Boost',
    'SoundCore Flare','SoundCore Icon Mini','SoundCore Icon+','SoundCore Mini 2','SoundCore Rave','SoundCore','Air3 Deluxe','Air3','Capsule3 Pro','H2','Life',
    'MAC','Mini Pro','Mini','RunFree Lite','T3 ANC','T3','True Air 2','True Capsule 2','TrueCapsule2','Truedot','TrueFree 2','TrueFree2 Classic','Truengine 3 SE','Arctis Pro','Monty','T35','T7','Ear Force Recon 50','Recon 50P','Recon 70','Recon 71','Stealth 700','Tx-Pr20','V9','Wireless Stereo Protable Speaker White','AirDots','Mi Basic S','Mi','Redmi Buds 3','GH-890','Z333','B20',
    'Eufy HomeVac S11 Go','Eufy RoboVac 11','Eufy RoboVac 11S','Eufy Robovac G10 Hybrid','Eufy RoboVac R450','HomeVac H30 Handheld','RoboVac 11C','Dura-Beam Deluxe','SDM-WD3238TG','WA10T5260BY','WW70T3020BS GU','WW80TA046AX GU','KC-G40Sa','SGW7200NLED','W6104-2','MB168B','VS197DE','E1916HV','GOB22FHD75IPS','19M35A-B','20MT48AF','22MP400','27MP400-B','M2394AJ','Occuwzz 15.6','193V5LSB2','271V8/89','B-LINE','F24T350FHM','LS19A330NHMXUE','SM-LS24F350FHM','RMMNT27NF','RAP-3WNP','BL-WN151',
    'DIR-825M','Mi Pro','N300','Dual Band Wireless Adapter Black/Yellow','GTMEDIA','Wireless-N Mini','WHW0303B-ME','AC5400','Archer T2U Nano','Archer T3U','RE305','TL-WA801N','TL-WN823N','TL-WR840N','UVC-NVR-2TB Unifi Video Recorder Network','AC650','Mi Repeater 2','Mi WiFi Router 4C','MFC-J3540DW','PT-H110','RP108','Selphy CP1300','EcoTank L3160','EcoTank L805','EcoTank L850','305 Ink Cartrige','DeskJet 2720','Envy 4520','MFP 178NW','MFP M283fdw','PhotoSmart 8050','WorkCentre 7855','TLP 3842','ZD220','ZD410','Nest Learning 3rd Gen',
    'A7 Plus','CM1000','CM495','CM500','CM513 Pro','K11','K91','KT2','Note 5 Plus','Pad','Q19','Tab E10','Tab E7','Tab M10',
    'Tab M10 Plus','Tab M7','Tab M8','U100','X12','Xperia Z4','Kindle EY21','Kindle Fire D01400','Kindle Paperwhite DP75SDI','Tab','Tab 3 Lite','Tab A 2019','Tab A6 2016','Tab A7 2020','Tab A7 Lite 2021','Tab A8 2021','Tab A9 2023','Tab Active 2','Tab Active 3','Tab S2','Tab S3','Tab S4',
    'Tab S5e','Tab S6','Tab S6 Lite','Tab S7','Tab S7 FE','Tab S7+','Tab Tab A','Tab Tab A8','iPad 2012','iPad 2017','iPad 2018','iPad 2019','iPad 2020','iPad 2021','iPad 2022','iPad Air 2013','iPad Air 2014','iPad Air 2019','iPad Air 2020','iPad Air 2022','iPad Mini 2012','iPad Mini 2013','iPad Mini 2014','iPad Mini 2015','iPad Mini 2017','iPad Mini 2019','iPad Mini 2021','iPad Pro 2015','iPad Pro 2016','iPad Pro 2017','iPad Pro 2018','iPad Pro 2020','iPad Pro 2021','MediaPad 2020',
    'MediaPad 2021','MediPad M','MediaPad M5 Lite','MediaPad T','MediaPad T10','MediaPad T10s','MediaPad T3','MediaPad T5','MediaPad T5 Kids Edition','Note 6','Pad 2021','Pad 2022','Tab 4','Quest','Gear VR Controller','PlayStation VR1 Bunlde with Camera','PlayStation VR1 Launch Bundle','Watch SE','Watch','Watch Ultra','Test Modal 3','Aspire 1 A114-32-C2VZ','Aspire ZG5','Aspire A314','Aspire A315','Aspire A315-51-39YY','Aspire A315-56382R','Aspire A315-56-594W','Aspire A315-58-523F','Aspire A315-59-55XS','Aspire 4736Z','Aspire A514','Aspire A514-53G-70DU','Aspire A514-55','Aspire A515-54G','Aspire A515-56G-53LQ','Aspire A515-58GM-58JZ',
    'Aspire 5750','Aspire A715-42G-R1DU','Aspire E5-575','Aspire V15 Nitro VN7-592G-75MF','Chromebook 314','Chromebook C738T','Chromebook N19Q2','Extensa 15-EX2519','Latitude 3510','Nitro 5 AN515','Nitro AN515-54-728C','Nitro AN515-55-558U','Nitro AN515-57-573','Nitro AN515-57-57G2','Nitro AN515-57-741C','Nitro AN515-58-762S','Nitro NG-AN515-55-74Z6','One S1003-100H','Predator Helios 300','Predator Helios Neo 16 PHN16-72-962U','ProBook 440 G8','Spin 1 SP111-34N-C2YP','Spin 3 N19W2','Spin 3 SP314-54N-58Q7','Swift 1 SF113-31-C3NY','Swift SF314-52','V V130-15IGM','MacBook Pro 16-inch','Asus K556U','Asus M15DA','Asus P1440FA-FQ2883','Asus X452CP-VX017H','Asus X509FA-EJ950T','Asus X515JP-BQ432W','Asus X515MA-BR912WS','Asus X540L','Asus X540U',
    'Asus X541UAK','Asus X550','E Series E406M','Eee PC 1215N','ROG Strix G15','ROG Strix G17','Transformer Book TP200SA','Transformer Book TP500L','TUF Dash FX516PC-HN558W','TUF FA506I','TUF FA506IHR-HN019W','TUF FX506H','TUF FX506L','TUF FX706HEB-HX114W','VivoBook 540NA-GQ017T','VivoBook A412D','VivoBook TP401MA-EC340TS','VivoBook TP470EZ-EC017T','VivoBook E1404GA-NK039W','VivoBook TP1400KA-BZ056WS','VivoBook K513E','VivoBook K513EA-AB54','VivoBook K513EQ-OLED107T','VivoBook S14','VivoBook S406U-ABM257T','VivoBook X1404VA-NK114W','VivoBook X507U','VivoBook X507UA-EJ001T','VivoBook X509J','VivoBook X540UB-DM407T','ZenBook UX463FA-AI048T','ZenBook UM3402YA','ZenBook UX3402ZA-OLED1P7W','2-in-1 Touch','PURA NS14A6','Z83II Mini PC','Ctroniq N14B','Ctroniq N14X','Chromebook 3180','Chromebook 3189','Elite 7300','G3 P89F','G5 5587','Inspiron 1545','Inspiron 3000','Inspiron 3168','Inspiron 3467','Inspiron 3477 All in One','Inspiron 3511','Inspiron 3521','Inspiron 3542','Inspiron 3552','Inspiron 3558','Inspiron 3567','Inspiron 3573','Inspiron 3580','Inspiron 3581','Inspiron 3582','Inspiron 3583','Inspiron 3593','Inspiron 5000','Inspiron 5010','Inspiron 521','Inspiron 5400 All in One','Inspiron 5406','Inspiron 5410','Inspiron 5423','Inspiron 5481','Inspiron 5510','Inspiron 5582','Inspiron 5584','Inspiron 7000','Inspiron 7306','Inspiron 7400','Inspiron 7577','Inspiron N4010','Inspiron N5010','Inspiron N5040','Inspiron N5110','Latitude D610','Latitude 3410','Latitude 5300','Latitude 5400','Latitude 5430','Latitude 7280','Latitude 7390','Latitude 7400','Latitude 7470','Latitude 7480','Latitude 7490','Latitude D500','Latitude D620','Latitude D630','Latitude E5570','Latitude E6220','Latitude E6230','Latitude E6400','Latitude E6410','Latitude E6420','Latitude E6420ATG','Latitude E6430','Latitude E6440','Latitude E7250','OptilPlex 7010','Vostro 3300','Vostro 3400','Vostro 3491','Vostro 3500','Vostro 3510','Vostro 3550','Vostro 3568','Vostro 3910','XPS 7390','XPS 9305','XPS 9380','HP 290 G1MT','HP 22-c0028in','Chromebook 11G3','Chromebook 14A-NA0020NR','Compaq 420','EliteBook 820 G1','EliteBook 820 G2','EliteBook 820 G3','EliteBook 840 G1','EliteBook 840 G3','EliteBook 840 G4','EliteBook 840 G6','EliteBook 8440P','EliteBook 8460P','EliteBook 8470P','EliteBook 850 G3','EliteBook Folio 1040 G3','EliteBook Folio 9470M','Envy 13-ad125tu','Envy 13-BA0002NE','Envy TouchSmart TouchSmart 23','Envy x360 13-AR0009NE','Envy x360 13-AY0010NE','Envy x360 15M-ED1013','Mini 110-1001TU','Notebook Notebook 15-bs015dx','Notebook 14-DK1022WM','Notebook 14-DQ0002DX','Notebook 14-DQ1037WM','Notebook 14-DQ1040WM','Notebook 14-DQ1055CL','Notebook 14-R002NE','Notebook 14S-DQ5029NE','Notebook 14S-FQ0017NE','Notebook 15','Notebook 15-AY131NE','Notebook 15-BS031WM','Notebook 15-BS154','Notebook 15-BS168CL','Notebook 15-DA0000NE','Notebook 15-DA0019NIA','Notebook 15-DA001NE','Notebook 15-DA0023NE','Notebook 15-DA0053WM','Notebook 15-DA0073WM','Notebook 15-DA0082CL','Notebook 15-DA1000NE','Notebook 15-DA1002NE','Notebook 15-DA1012NE','Notebook 15-DA1013NE','Notebook 15-DA1016NE','Notebook 15-DA2197NIA','Notebook 15-DB0000NE','Notebook 15-DB0014NE','Notebook 15-DB1200NY','Notebook 15-DW0015NE','Notebook 15-DW0016NE','Notebook 15-DW1001WM','Notebook 15-DW1380NIA','Notebook 15-DW2003NE','Notebook 15-DW2030NE','Notebook 15-DW2081NE','Notebook 15-DW3033DX','Notebook 15-DW3389NE','Notebook 15-DY0013DX','Notebook 15-DY1031WM','Notebook 15-DY1032WM','Notebook 15-DY-1091WM','Notebook 15-DY1713MS','Notebook 15-DY1731MS','Notebook 15-DY2078NR','Notebook 15-DY2791WM','Notebook 15-EF1073WM','Notebook 15-M9V38PA','Notebook 15-R210NE','Notebook 15-RA0008NIA','Notebook 15-RA006NE','Notebook 15-RA008NIA','Notebook 15-RA009NX','Notebook 15S-DU2100TU','Notebook 15S-EQ0011NE','Notebook 15S-EQ0014NE','Notebook 15S-EQ20011NE','Notebook 15S-EQ20014NE','Notebook 15S-FQ1019NE','Notebook 15S-FQ5','Notebook 15S-FQ5287NIA','Notebook 15T-DW200','Notebook 240 G8','Notebook 245 G7','Notebook 250 G5','Notebook 250 G6','Notebook 250 G7','Notebook 250 G8','Notebook 290 G2','Notebook 3165NGW','Notebook 3168NGW','Notebook 430 G2','Omen 15-dc1069wm','Omen 15-DH0009NE','Omen 15-DH0023NE','Omen 15-DH1020NE','Omni 200','Pavilion Pavilion 15-ab165us','Pavilion 14-CE','Pavilion 14-CE0001NE','Pavilion 15-CS0053CL','Pavilion 15-CX0019NE','Pavilion 15-DK1000NE','Pavilion 15-DK2049NE','Pavilion 15-DW1O11NE','Pavilion 15-P216NE','Pavilion 15t-eb0098nr','Pavilion 15t-eg2053dx','Pavilion DV1000','Pavilion DV6','Pavilion x360 14-dh1021ne','Pavilion x360 14-dh1011ne','Pavilion x360 14-dh0013ne','Pavilion x360 14-dh1036tx','Pavilion x360 14-DH0001NE','Pavilion x360 14-DH0011NE','Pavilion x360 14-DH01026NE','Pavilion x360 14-DH1007NE','Pavilion x360 14-DH1026NE','Pavilion x360 14-DH1029NE','Pavilion x360 14-DW1002NE','Pavilion x360 14M-DW0013DX','Pavilion x360 14M-DW0023DX','Pavilion x360 14T-DH100','Pavilion x360 DH003NE','ProBook 430 G2','ProBook 450 G3','ProBook 4530S','ProBook 4540S','ProBook 6450B','Spectre 13 (G1)','Spectre x360 14-ef0013dx','Spectre x360 13-AW2002TU','Spectre x360 13T-AP000','Spectre x360 14-EA1016NX','Stream 11-y002na','Stream 11-ak0012dx','Stream 11-AK1010NR','MateBook 13','MateBook D14','MateBook D15','MateBook D16','Zed Air','Zed Air CX5','Zed Air Mini','Zed Note 14i','ZedNote II','ZedNote Prime','InnJoo N2 N2','Chromebook 100e','Flex 4 45712','G G40-80','G G50-30','G G50-70','G G50-80','IdeaCentre A340-22IGM All in One','IdeaPad 1 11ADA05','IdeaPad 1 11IGL05','IdeaPad 1 14IGL05','IdeaPad 1 14IGL06','IdeaPad 1 14IGL7','IdeaPad 100-15','IdeaPad 110-15ISK','IdeaPad 120S-11IAP','IdeaPad 130','IdeaPad 130-14IKB','IdeaPad 130-15IKB','IdeaPad 3 14ADA05','IdeaPad 3 14IGL05','IdeaPad 3 14IIL05','IdeaPad 3 15IIL05','IdeaPad 3 15IML05','IdeaPad 3 15ITL6','IdeaPad 3 Chromebook 11IGL05','IdeaPad 3 Chromebook','IdeaPad 300-15ISK','IdeaPad 320-14IKB','IdeaPad 330-14IGM','IdeaPad 330-151KB','IdeaPad 330-15IGM','IdeaPad 330-15IKB','IdeaPad 330S-14IKB','IdeaPad 330S-15IKB','IdeaPad 4 14IIL05','IdeaPad 5 14ARE05','IdeaPad 5 14ITL05','IdeaPad 5 15IIL05','IdeaPad C340-14IWL','IdeaPad Flex 14','IdeaPad Flex 5 15ITL05','IdeaPad L3 15IML05','IdeaPad L340-15IRH','IdeaPad S130-11IGM','IdeaPad S145-14IWL','IdeaPad S145-15AST','IdeaPad S145-15IGM','IdeaPad S340-15IIL','IdeaPad Slim 1 14AST','IdeaPad V14 IGL','IdeaPad V145-15AST','IdeaPad Y5070','IdeaPad Z470','IdeaPad Z500','Legion 5 15ITH6H','Legion Y545','Satellite U400-10L','ThinkBook 13s-IWL','ThinkBook 15 G2 ITL','ThinkBook 15-IML','ThinkCentre E63z','ThinkPad E15','ThinkPad E580','ThinkPad E590','ThinkPad T420s','ThinkPad T430i','ThinkPad T430s','ThinkPad T440','ThinkPad T450','ThinkPad T460s','ThinkPad X1 Carbon','ThinkPad X1 Yoga','ThinkPad X220','ThinkPad X270','V V14-IIL','V V15-IIL','Yoga 300-11IBR','Yoga 330-11IGM','Yoga 510-14ISK','Yoga 520-14IKB','Yoga 6 13ARE05','Yoga 920-13IKB','Yoga Book X91','Yoga C740-14IML Convertible','Yoga C940-14IIL Convertible','Yoga Slim 7 13ITL5','Yoga Slim 7 14ITL05','Yoga Slim 7 Pro 14IHU5','Surface Book 2','Suface Go 10 inch','Surface Laptop 3','Surface Laptop Go','Surface Pro 3','Surface Pro 5','Surface Pro 6','Surface Pro 7','Surface Pro 7+','Surface Pro 9','TULPAR T5 V18.1','Bravo 15 A4DDR','Modern 14 B10RASW','Modern 14 B4MW-091AE','Modern 14 B5M','Notebook PC MS-16J9','Sword 15 A11UD','Book 13','Macbook Air 2020','MacBook Pro','ThinkPad Helix Ultrabook Pro','Chromebook Series 3 303C XE303C12','Chromebook 3 XE501C13-S02US','Chromebook 4 XE310XBA-K01US','Galaxy Book 750XDA-KD5UK','Portege Z10t','Satellite R630 14T','Z06','A8PD','A8QC','Nebula Apollo','Nebula Capsule II','Nebula Capsule Pro','Adaptor LPE10','Nebula Mars II','Nebula Prizm II Pro','Nebula Vega','Battery Case Cover','Battery LPE10','Brave 10','MasterKeys Lite','Speed EX','Dell Laptop & Desktop','T9','DPF-A710','G212','Fader','A36','GP80','GTX300','K-03','LED','M1','R5 Edition','USB X','H8','GameNote','HV-MS672','Hero 10','CS10','M10','H300','V100','Incase Power','K55','G Pro X Superlight','G203','G213 PRODIGY','G305','G502 Hero','G502 X','G600','G604','GS12 Carbon','M90','MK270','MK295','Arc Touch','Interceptor DS200','PB1040024S02BRB','Power Tube','PowerCore','PowerCore Essential','PowerCore II','PowerCore III Sense','PowerCore Select','PowerCore Slim','PowerCore+','PowerWave','XD200C','XD30','V500PRO-87','Deathadder Essential','Deathadder','Firefly V2','Goliathus','Huntsman V2 Tenkeyless','Huntsman V2 TKL','Naga Pro','K550-1 Yama','Kumara','M908 Impact','K12+','Burst Core','The Freestyle','PrismCaps','Chromecast 3','Chromecast','Chromecast Ultra','Fire tV Stick','GT Media V8 NOVA DVB-S2','MAG 254/255w2','Mi Android 9.0 TV Stick','Mi Box 4C','Mi Box S','Q Plus Android Smart','R14K Android Smart','RK3229 Android','Video Car','X96 Mini Android','ACH114EU','Pro (2022)','KB2392-V1','MX Impact 500','UE10053','Vectra','Veger2','Venom','WP04','MK-503 KIT','PS5 Call Of Duty: Black Ops Cold War','PS4 /XOne /XSeries /switch /PC Gaming Headset A40 TR','PS4/PC C40 TR','Rog Balteus Vertical Gaming Mouse Pad','Rog Phone 2 Kunai Gamepad','Rog Phone 3 Kunai Gamepad','Rog Sheath Extended Gaming Mouse Pad','Rog Twinview Dock 2','Flashback 7 Classic Game','PS4 Days Gone','Elgato Game Capture','Zen Converter','PS4 Console Storage Stand Kit','PS4 Cooling Stand','PS4 Dual Charging Dock','PS4 Slim/Pro Charging Stand for Controller','PS4 USB Hub','PS4/PS5 FIFA 2023','PS4 Fortnite','Skipper Racing Wheel for PC','F2 Firestick Grip','F4 Falcon Mobile Gaming','G174BT','G5 with Trackpad and Customizable Fire Buttons Moba FPS RoS','T1S All-in-One','T4 2.4 GHz','8 Bit Mini TV Game Console','8 Bit Retro Handheld Game Player','Controller Skin Plus','Xbox one Controller Power Skin Case','XXL Extended Gaming Mouse Pad 18" x 36"','Horipad','PS4 Apex Wired RWA Racing Wheels and Pedal','PS4 Apex Wireless RWA Racing Wheels and Pedal','PS4 Onyx','Switch Dual USB Playstand','Switch Pikachu D-Pad','Switch Split Pad Pro','Xbox One Racing Wheel Overdrive','Xbox Series X Racing Wheel Overdrive','Xbox Series X Solor Charging Station','Pavilion 400 Wired Over-Ear Gaming Headphones','PS4/Xbox P6 Keyboard and Mouse Adapter','PS4 Marvel\'s Spider Man','PG - 9087 Retractable','Telescope','Tomahawk','Wireless Controller','Computer Kit 1010-01 A Computer Anyone Can Make','GTX300 Suspension Rainbow Light Gaming Mouse And Keyboard','F310 Wired Gamepad','F710','PS5/PS4 G923 Wired Racing Wheel and Pedal','PS5/PS4/PS3 G29 Wired Driving Force Racing Wheel and Pedal','X52 Flight Control System','Xbox/PC G920 Wired Driving Force Racing Wheel and Pedal','Xbox/PC G923 Wired Racing Wheel and Pedal','Xbox 360','Xbox 360 Kinect Sensor','Xbox Games','Xbox One','Xbox One Call of Duty: Modern Warfare Remastered','Xbox One Gears Of War 4','Xbox One S','Xbox One X','Xbox Series S','Xbox Series X','Xbox Series X/S','Xbox Wireless Controller','PS4 Asymmetric','PS4 Compact','PS4 Revolution Pro 2','PS4 Revolution Pro 3','PS4 Revolution Pro','PS4 Revolution Unlimited Pro','PS4/PC illuminated Compact','Xbox/PC BB5108 PCGC-200WL','Xbox/PC NC5108 PCGC-200WL','FIFA 23 Legacy Edition','Mario Kart 8 Deluxe','Super Smash Bros Ultimate','Switch Animal Crossing: New Horizons','Switch Carrying Case','Switch Dock','Switch Enhanced','Switch FIFA 2020 Legacy Edition','Switch Joy Con','Switch Lite','Switch Nano Enhanced','Switch OLED','Switch Pro','Switch Sports','Switch V1','Switch V2','Switch W2K18','Team Sonic Kart Racing','Nintendo Wii 512MB Console White','Yoshi\'s Crafted World','Red Magic E-Sports Handle','GTX1060-3GD5 Nvidia Graphics Card','PS4 Gaming Data Bank','Switch Lite Comfort Grip','Switch Enhanced running Mario','Switch Mario Themed','Xbox Series X/S Dual charging Station','Xbox Series X/S Switch Enhanced','Xbox Wireless Controller Dual Charging Station','Clix-6 Wireless Gaming Mouse','Clix-8 Wireless Optical Gaming Mouse','Crusader Unidirectional Hyper-Sensitive Cardioid Gaming Microphone','USB Gaming Microphone','PS4/PS3/Xbox one/PC V3II 4-In-1 Wired Steering Wheel','Basilisk V2 Wired Ergonomic Gaming Mouse','Deathadder Lite Wired Gaming Mouse','Deathadder v2 Chroma Wired Gaming Mouse','Goliathus Chroma Soft Gaming Mouse Pad','iPhone Kishi V2 Mobile','Mouse Bungee V3','PS5 Quick Charging Stand','RaijuTournament Edition','Viper Ultimate Wireless Gaming Mouse','Viper Wired Optical Sensor Gaming Mouse','Xbox Wolverine V2','H350 Pandora RGB Wired Gaming Headset','PS4 Grand Theft Auto Premium Edition','Mega Drive 2','Mega Drive Control Pad','PS4 Call of Duty WWII','DualShock 4 Back Button Attachment','PlayStation','PlayStation Portable','PS 3 DualShock 3','PS4 Assassin\'s Creed Origins','PS4 Battlefield 1','PS4 Carnival Games','PS4 Crash Bandicoot N Sane Trilogy','PS4 Crash Team Racing + Crash Bandicoot N.Sane Trilogy','PS4 Detroit Become Human','PS4 DualShock 4','PS4 F1 2019','PS4 Far Cry 4','PS4 FC 24 Sports','PS4 FIFA 16','PS4 FIFA 17','PS4 FIFA 18','PS4 FIFA 19','PS4 FIFA 20','PS4 Final Fantasy Type-0 HD','PS4 Fortnite Minty Legends','PS4 Infamous Second Son','PS4 Mass Effect Legendary Edition','PS4 NBA 2K23','PS4 Need For Speed Payback','PS4 Overwatch','PS4 Player Unknown\'s Battlegrounds','PS4 Ratchet & Clank','PS4 Resident Evil 4','PS4 Riders Republic','PS4 Rocket League','PS4 The Evil Within 2','PS4 Uncharted 4: A Thief\'s End','PS4 Uncharted The Nathan Drake Collection','PS4 Until Dawn','PS4 VR Worlds','PS4 VR Worlds Game','PS4 Watch Dogs 2','PS4 WWE 2K Battlegrounds','PS4 WWE 2K17','PS4/PS5 Assassin\'s Creed Odyssey','PS4/PS5 Minecraft','PS5 Call of Duty Modern Warfare II','PS5 Dead Space','PS5 DualSense','PS5 FIFA 21','PS5 Final Fantasy XVI','PS5 God of War Ragnarok','PS5 Gran Turismo 7','PS5 HD Camera','PS5 Hogwarts Legacy','PS5 Mortal Kombat 1','PS5 Prince of Persia The Lost Crown','PS5 Spider-Man: Miles Morales','PS5 Street Fighter','Apple Nimbus+','PS4 Gator Claw','Game Box Plus 400 in 1 Retro Mini Gameboy','PC TWCS Throttle Weapon Control System','PS4 T-Flight Hotas 4 Joystick','PS4/PS3 /PC T300 Ferrari Integral Racing Wheel','PS4/PS3 /PC T300 RS Racing Wheel','PS4/PS3 TH8A Add-On Shifter','PS5/PS4/PC T150 PRO Racing Wheel and Pedals','PS5/PS4/PC T150 RS Racing Wheel and Pedals','PS5/PS4/PC T80 Ferrari 488 GTB Racing Wheel with Pedals','Xbox T80 Ferrari 548 GTB Racing Wheel with Pedals','Xbox TMX Pro Steering Wheel With Pedal Set','Elyte Scorpio Usb Hub & Gaming Mouse Cable Holder','Xbox/PC Recon TBS-0700-02','Xbox/PC Recon','Xbox FIFA 18','S70','EufyCam','EufyCam 2 Pro','EF-S 18-135mm f/3.5-5.6 IS USM','EF-S 18-55mm f/3.5-5.6 IS','Mavic Mini','Mini 2 SE','RS 3 Mini','Generic 1080p','Generic 1080p Wi-Fi','Generic 2 Megapixel','Generic','Generic Wi-Fi','Lux Junior','DS-2CD1021-I','Hometrol Wi-Fi','IBRAND','1080p Webcam','2K 30FPS Webcam','4K 30FPS Webcam','720p Webcam','70-300mm f/4.5-6.3 Di III RXD','AT-X 100mm f/2.8 PRO D Macro','V380','Home Security Camera 360° 1080P','Wireless Outdoor Security Camera 1080p','Home Security HD Camera','1080p Waterproof Wi-Fi HD','iPhone 16e','iPhone 16','iPhone 16 Plus','iPhone 16 Pro','Honor Magic 6 Pro','Galaxy Z Fold5','iPhone 17','Galaxy S25 Ultra','iPhone 12 Mini','ExpertBook B1402CV','iPhone 17 Pro','iPhone 17 Pro Max','Spark 8','Lattitude D510','Probook 650 G4','Aspire E5-575G','Envy Notebook DV6','Lattitude E6430','Compaq RD01-D480','MacBook Air 2020 A2337','MI 11','MI 11T','MI 11T Pro','Poco X3 NFC','Nokia 7','Galaxy A04e','Oppo A16e','Honor 10','Galaxy Wide 5','A15','Pixel 4A','Motorola Z4','Redmi 5 Plus','F11 Pro','Grand 2c','Meizu V8','Galaxy Z Flip7','Satellite C850-F32Q','Aspire 4741','Yoga 7 2-in-1','Vivo X7 Plus','Honor 8C','A16e','Nokia 2','Galaxy J4','Galaxy J3','A03','Oppo A16K','Vivo V20','Vivo V21e','Vivo 2015','Vivo Y93','Vivo Y73s','Vivo 1820','Vivo Y21','Oppo A54','Oppo A5s','Galaxy A9 Pro','Galaxy M22','Galaxy M 11','Galaxy A 02s','Onn Focus','MacBook A1534','MacBook Air A1466','MacBook Air A2337','MacBook Air A2179','MacBook Air A2681','MacBook Air A1304','MacBook Air A1932','MacBook Pro A1708','MacBook Pro A1989','MacBook Pro A2338','MacBook Pro A1278','MacBook Pro A1990','MacBook Pro A2485','MacBook Pro A1502','MacBook Pro A1707','Ideapd 5 pro 14IAP7','Spark 4','Realme 7','Realme C2','Honor Play3','Techno Pop 5','Oppo A12','Y21','Redmi A2 Plus','Oppo A16','Meizu M3 Max','Redmi Y2','Samsung Galaxy Grand prime pro','Samsung Galaxy On7','Samsung Galaxy J7','Realme GT Master','Oppo A95','Oppo A56','Realme 9i','Realme C11','Vivo Y85','Oppo A1','Vivo Y67 4GB 64GB','Huawei Y6','Huawei P Smart','Huawei Nova 3i','Galaxy KT','Galaxy J8','Galaxy Wide 3','Galaxy A6 Plus','Honor Magic 7 Pro','Magic Pad 2','Vivo Y71A','Galaxy M23','Vivo Y66','Galaxy A10e','Honor 8X','Oppo A4 Pro','Latitude 7200','Envy 14-J104TX','MacBook Pro A1481','VivoBook X1404Z','MacBook Pro A2159','Latitude 7310','Latitude 5421','MacBook Air A2617','Surface Go','IdeaPad 320-141KB','MacBook Air A1279','EliteBook x360 1040 G7','Surface Pro 4','ideapad 720S-13IKB','MateBook B0HB-WAX9','ThinkPad T470','Asus X409J','ThinkPad X1','ExpertBook B1402CB','IdeaPad Slim 3 15IRH8','Yoga C740-14iml 81tc','MacBook Pro 2017','Watch Series 3','Watch Series 4','Watch Series 5','Watch Series 6','Watch Series 7','Honor Band 4','Pavilion x360 14-DH0015NE','ZBook Firefly 15 G7','MI Band 4','Oppo F1s','Oppo Reno 6','Oppo Reno 6Z','Redmi Note 13','Redmi Watch 5','Galaxy A55','Galaxy Fit2','Galaxy Grand Prime Pro','Galaxy Watch 3','Galaxy Watch 4','Galaxy Watch 7','Gear S2 Classic','Tecno Spark 5 Air','Tecno Spark 8','Watch 2 SpO2','Galaxy F04','Galaxy A04','Galaxy Wide 4','Redmi 9T','VivoY21','Vivo Y52s','Tecno Camon 16','Moto e13','Infinix Hot 12','Poco M2','Realme 8','ZTE Blade A71','Itel P55 Plus','X Series','V Series','PlayStation 5 DualSense','Stream Deck','F Series','Crash Bandicoot','HDM-T156','Taohsuan Adapter','Galaxy Buds R510L','Suunto Spartan Sport','Poco M7 Pro','iMac A1225','Sony Xperia 1 mark5','iPad Pro 2024','Galaxy A56','Galaxy Watch 6'

}

COLOR_DICTIONARY = {
    # Black family
    'black', 'jet black', 'onyx', 'midnight', 'phantom black', 'carbon black', 
    'obsidian', 'space black', 'cosmic black', 'stellar black', 'graphite',
    'charcoal', 'ebony', 'raven',
    
    # White family
    'white', 'pearl white', 'alpine white', 'glacier white', 'ceramic white',
    'ivory', 'snow white', 'chalk white', 'silver', 'platinum', 'metallic silver',
    'stainless steel', 'chrome', 'frost white',
    
    # Blue family
    'blue', 'sapphire blue', 'ocean blue', 'navy blue', 'cobalt blue', 
    'arctic blue', 'sky blue', 'baby blue', 'azure', 'ice blue', 'midnight blue',
    'royal blue', 'deep blue', 'pacific blue',
    
    # Red family
    'red', 'crimson red', 'ruby red', 'scarlet', 'vermillion', 'rose red',
    'product red', 'coral red', 'fiery red', 'burgundy', '(product)red',
    
    # Green family
    'green', 'forest green', 'emerald green', 'olive green', 'mint green',
    'alpine green', 'hunter green', 'army green', 'sage green', 'lime green',
    'pine green',
    
    # Gold family
    'gold', 'rose gold', 'champagne gold', 'sunset gold', 'pink gold',
    'blush gold', 'yellow gold', 'starlight gold',
    
    # Purple family
    'purple', 'lavender', 'violet', 'orchid', 'lilac', 'amethyst',
    'deep purple', 'royal purple', 'eggplant', 'plum', 'mauve',
    
    # Gray family
    'gray', 'grey', 'graphite', 'charcoal', 'slate', 'steel gray',
    'space gray', 'space grey', 'metallic gray', 'titanium', 'ash gray',
    
    # Brown family
    'brown', 'espresso brown', 'chocolate brown', 'cognac', 'tan', 'taupe',
    
    # Pink family
    'pink', 'blush pink', 'rose pink', 'coral pink', 'hot pink', 'magenta',
    
    # Orange family
    'orange', 'sunset orange', 'coral orange', 'tangerine', 'amber',
    
    # Yellow family
    'yellow', 'sunflower yellow', 'golden yellow', 'lemon yellow',
    
    # Multi-color
    'rainbow', 'multicolor', 'prism', 'gradient',
    
    # Special editions
    'starlight', 'sunlight', 'moonlight', 'aurora', 'northern lights'
}

# Color synonyms for better matching
COLOR_SYNONYMS = {
    'black': {'jet black', 'onyx', 'midnight', 'phantom black', 'carbon black', 'obsidian'},
    'space black': {'space gray', 'cosmic black', 'stellar black'},
    'midnight':  {'night', 'noir', 'phantom black'},
    'white': {'pearl white', 'alpine white', 'glacier white', 'ceramic white', 'ivory'},
    'silver': {'platinum silver', 'metallic silver', 'stainless steel', 'chrome'},
    'blue':  {'sapphire blue', 'ocean blue', 'navy blue', 'cobalt blue', 'arctic blue'},
    'sky blue': {'baby blue', 'azure', 'ice blue'},
    'midnight blue': {'navy', 'deep blue', 'royal blue'},
    'red': {'crimson red', 'ruby red', 'scarlet', 'vermillion', 'rose red', '(product)red', 'product red'},
    'product red':  {'red', '(red)', 'productred'},
    'green': {'forest green', 'emerald green', 'olive green', 'mint green'},
    'alpine green': {'forest green', 'hunter green', 'army green'},
    'gold': {'rose gold', 'champagne gold', 'sunset gold', 'pink gold'},
    'rose gold': {'pink gold', 'blush gold'},
    'purple': {'lavender', 'violet', 'orchid', 'lilac', 'amethyst'},
    'deep purple': {'royal purple', 'eggplant', 'plum'},
    'gray': {'grey', 'graphite', 'charcoal', 'slate', 'steel gray'},
    'space gray': {'space grey', 'metallic gray', 'titanium gray'},
}

# Site configuration for Amazon sites getting images
SITE_CONFIG = {
    "amazon.ae": {
        "SEARCH_URL": "https://www.amazon.ae",
        "PRODUCT_TITLE": (By.ID, "productTitle"),
        "IMG_CONTAINER": (By.ID, "altImages"),
        "IMG_SELECTOR": "#altImages img",
        "CSV": "scrape_results_Amazon_ae_R1.csv",
        "OUTPUT_DIR": r"E:\R3 Factory\Product_images\Super Variant\Rounds1\Amazon.ae_laptop",
        "IMG_PROCESS": lambda url: re.sub(r'\._.*?_\.', '._SL500_.', url) if url else ""
    },
    "amazon.in": {
        "SEARCH_URL": "https://www.amazon.in",
        "PRODUCT_TITLE": (By.ID, "productTitle"),
        "IMG_CONTAINER": (By.ID, "altImages"),
        "IMG_SELECTOR": "#altImages img",
        "CSV": "scrape_results_Amazon_in_R1.csv",
        "OUTPUT_DIR": r"E:\R3 Factory\Product_images\Super Variant\Rounds1\Amazon.in_laptop",
        "IMG_PROCESS": lambda url: re.sub(r'\._.*?_\.', '._SL500_.', url) if url else ""
    },
    "amazon.com": {
        "SEARCH_URL": "https://www.amazon.com",
        "PRODUCT_TITLE": (By.ID, "productTitle"),
        "IMG_CONTAINER": (By.ID, "altImages"),
        "IMG_SELECTOR": "#altImages img",
        "CSV": "scrape_results_Amazon_com_R1.csv",
        "OUTPUT_DIR": r"E:\R3 Factory\Product_images\Super Variant\Rounds1\Amazon.com_Laptop",
        "IMG_PROCESS": lambda url: re.sub(r'\._.*?_\.', '._SL500_.', url) if url else ""
    },
    "noon": {
        "SEARCH_URL": "https://www.noon.com/uae-en/",
        "SEARCH_BOX": (By.ID, "search-input"),
        "RESULTS": (By.CSS_SELECTOR, 'div[data-qa="plp-product-box"]'),
        "TITLE": (By.CSS_SELECTOR, 'h2[data-qa="plp-product-box-name"]'),
        "PRODUCT_TITLE": (By.CLASS_NAME, "ProductTitle-module-scss-module__EXiEUa__title"),
        "IMG_CONTAINER": (By.CSS_SELECTOR, "div.GalleryV2_thumbnailInnerCtr__i7TLy"),
        "IMG_SELECTOR": "button.GalleryV2_thumbnailElement__3g3ls img",
        "LINK": (By.CSS_SELECTOR, 'a.ProductBoxLinkHandler_productBoxLink__FPhjp'),
        "CSV": "scrape_results_noon.csv",
        "OUTPUT_DIR": r"E:\R3 Factory\Product_images\Super Variant\Rounds1\Noon_Laptop",
        "IMG_PROCESS": lambda url: re.sub(r'\._.*_\.', '._SL500_.', url) if url else ""
    }
}
