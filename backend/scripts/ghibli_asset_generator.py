#!/usr/bin/env python3
"""
Studio Ghibli-Inspired RPG Asset Generator for Vocational Education Platform
Generates optimized prompts for AI image generation APIs
"""

import json
import csv
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

@dataclass
class AssetPrompt:
    category: str
    asset_type: str
    name: str
    prompt: str
    negative_prompt: str
    dimensions: str
    style_notes: str

class GhibliRPGAssetGenerator:
    def __init__(self):
        self.base_style = """Studio Ghibli-inspired RPG art style, hand-painted watercolor textures, 
        soft painterly brushstrokes, warm fantasy colors, organic linework, dreamlike atmosphere, 
        detailed environmental elements, whimsical charm, high resolution, professional game art quality"""
        
        self.negative_prompts = """harsh lighting, hyper-realistic, photographic, overly dark, 
        aggressive colors, rigid geometry, anime eyes, low quality, blurry, pixelated, 
        modern corporate style, sterile design"""
        
        # Define the 14 training package guilds
        self.guilds = {
            "business": {
                "name": "The Merchant Guild",
                "symbol": "golden scale and ink quill",
                "colors": "warm golds, rich browns, parchment yellows",
                "environment": "bustling trade district with scrolls, ledgers, market stalls",
                "packages": ["BSB", "FNS"],
                "district_name": "Merchant District",
                "levels": {
                    "cert1": {"name": "Market Alleys", "desc": "small market alleys with introductory business stalls"},
                    "cert2": {"name": "Merchant Halls", "desc": "larger merchant halls with financial strategy chambers"},
                    "cert3": {"name": "Chambers of Commerce", "desc": "grand chambers of commerce with negotiation training rooms"},
                    "cert4": {"name": "Guild Headquarters", "desc": "grand merchant guild headquarters with leadership mastery halls"}
                },
                "buildings": ["law offices", "banks", "trade houses", "market stalls", "guild banners"]
            },
            "health": {
                "name": "The Healer's Order", 
                "symbol": "lotus flower and glowing hands",
                "colors": "soft greens, healing blues, lotus pink",
                "environment": "tranquil meditation garden with nature and wellness spaces",
                "packages": ["CHC", "HLT", "SIS"],
                "district_name": "Sanctuary Gardens",
                "levels": {
                    "cert1": {"name": "Botanical Paths", "desc": "outer botanical paths with introductory health course gardens"},
                    "cert2": {"name": "Healing Sanctuaries", "desc": "inner healing sanctuaries with fitness and therapy chambers"},
                    "cert3": {"name": "Clinic Halls", "desc": "large clinic halls with mental health counseling rooms"},
                    "cert4": {"name": "Healer's Monastery", "desc": "grand healer's monastery with professional healthcare mastery temples"}
                },
                "buildings": ["herbal apothecaries", "therapy chambers", "meditation gazebos", "wellness shrines", "flowing rivers"]
            },
            "construction": {
                "name": "The Forge Keepers",
                "symbol": "blacksmith's hammer and anvil", 
                "colors": "iron grays, forge oranges, ember reds",
                "environment": "massive guild hall with glowing furnaces and metalworks",
                "packages": ["CPC", "RII"],
                "district_name": "Forge Alley",
                "levels": {
                    "cert1": {"name": "Metal Workshops", "desc": "outer metal workshops with introductory carpentry and plumbing stations"},
                    "cert2": {"name": "Building Sites", "desc": "stone-building sites with intermediate construction scaffolding"},
                    "cert3": {"name": "Guildmaster Forge", "desc": "guildmaster forge with advanced trades and engineering equipment"},
                    "cert4": {"name": "Architectural Chamber", "desc": "massive architectural chamber with leadership industry mastery halls"}
                },
                "buildings": ["blacksmith stalls", "blueprint archives", "scaffolding yards", "glowing furnaces", "industrial machinery"]
            },
            "education": {
                "name": "The Scholar's Assembly",
                "symbol": "parchment scroll and ink quill",
                "colors": "wisdom purples, ancient golds, parchment cream",
                "environment": "grand library temple with ancient tomes and mystical study rooms",
                "packages": ["TAE"],
                "district_name": "Scholar's Corridor",
                "levels": {
                    "cert1": {"name": "Study Gardens", "desc": "open study gardens with fundamental teaching technique pavilions"},
                    "cert2": {"name": "Lecture Halls", "desc": "inner lecture halls with instructional strategy chambers"},
                    "cert3": {"name": "Master's Study", "desc": "master's study rooms with high-level curriculum creation libraries"},
                    "cert4": {"name": "Scholar's Sanctum", "desc": "grand scholar's sanctum with leadership mastery in training temples"}
                },
                "buildings": ["archives", "examination chambers", "wisdom shrines", "ancient tomes", "parchment scrolls"]
            },
            "electro": {
                "name": "The Arcane Engineers",
                "symbol": "charged lightning rune and metal circuit",
                "colors": "electric blues, copper bronze, energy white",
                "environment": "high-tech workshop combining futuristic and ancient designs",
                "packages": ["UEE", "MSM"],
                "district_name": "Cybernetics Plaza",
                "levels": {
                    "cert1": {"name": "Data Kiosks", "desc": "outer data kiosks with fundamental programming terminals"},
                    "cert2": {"name": "Cyber Towers", "desc": "cyber towers with web development and security laboratories"},
                    "cert3": {"name": "Algorithm Labs", "desc": "algorithm labs with software mastery workstations"},
                    "cert4": {"name": "AI Core", "desc": "grand AI core with data science expertise command center"}
                },
                "buildings": ["holographic workbenches", "encryption vaults", "digital academies", "floating UI interfaces", "circuit pathways"]
            },
            "beauty": {
                "name": "The Artisan Collective",
                "symbol": "painted fan and silk ribbon",
                "colors": "elegant pastels, silk whites, cherry blossom pink",
                "environment": "floating tea house where artisans perfect their craft",
                "packages": ["SHB"],
                "district_name": "Artisan Pavilion",
                "levels": {
                    "cert1": {"name": "Apprentice Workshops", "desc": "ground-level apprentice workshops with basic beauty technique stations"},
                    "cert2": {"name": "Artisan Studios", "desc": "elevated artisan studios with advanced styling chambers"},
                    "cert3": {"name": "Master's Gallery", "desc": "master's gallery with creative technique showcase rooms"},
                    "cert4": {"name": "Grand Pavilion", "desc": "floating grand pavilion with artistic mastery and business leadership halls"}
                },
                "buildings": ["styling stations", "color mixing chambers", "mirror galleries", "silk banners", "floating platforms"]
            },
            "hospitality": {
                "name": "The Wayfarer's Lodge",
                "symbol": "compass and steaming cup",
                "colors": "warm tavern browns, welcoming oranges, hearth reds",
                "environment": "cozy inn where travelers and hosts exchange stories",
                "packages": ["SIT"],
                "district_name": "Wayfarer's Route",
                "levels": {
                    "cert1": {"name": "Traveler Inns", "desc": "outer traveler inns with introductory hospitality course rooms"},
                    "cert2": {"name": "Restaurant Streets", "desc": "bustling restaurant streets with advanced customer service dining halls"},
                    "cert3": {"name": "Festival Grounds", "desc": "festival grounds with luxury hospitality technique pavilions"},
                    "cert4": {"name": "Grand Lodge", "desc": "wayfarer grand lodge with leadership in tourism mastery chambers"}
                },
                "buildings": ["guesthouses", "tavern dining halls", "cultural exchange markets", "festival decorations", "warm hearth fires"]
            },
            "technology": {
                "name": "The Codecasters",
                "symbol": "floating hologram and data crystal",
                "colors": "digital blues, matrix greens, crystal whites",
                "environment": "digital sanctuary with glowing screens and logic circuits",
                "packages": ["ICT"],
                "district_name": "Digital Sanctum", 
                "levels": {
                    "cert1": {"name": "Code Terminals", "desc": "basic code terminals with fundamental programming interfaces"},
                    "cert2": {"name": "Development Labs", "desc": "development labs with web and application creation workstations"},
                    "cert3": {"name": "Systems Core", "desc": "systems core with advanced networking and security command centers"},
                    "cert4": {"name": "Master Sanctum", "desc": "master sanctum with enterprise technology leadership chambers"}
                },
                "buildings": ["server racks", "holographic displays", "data streams", "coding workstations", "digital archives"]
            },
            "manufacturing": {
                "name": "The Mechanist Brotherhood",
                "symbol": "clockwork gear and blueprint",
                "colors": "industrial grays, blueprint blues, brass yellows",
                "environment": "sprawling industrial complex filled with machinery",
                "packages": ["MEM", "MSA"],
                "district_name": "Manufacturing District",
                "levels": {
                    "cert1": {"name": "Assembly Lines", "desc": "basic assembly lines with introductory manufacturing processes"},
                    "cert2": {"name": "Machine Halls", "desc": "machine halls with intermediate engineering and production techniques"},
                    "cert3": {"name": "Engineering Core", "desc": "engineering core with advanced manufacturing systems and quality control"},
                    "cert4": {"name": "Master's Complex", "desc": "master's complex with production leadership and innovation laboratories"}
                },
                "buildings": ["conveyor systems", "testing chambers", "blueprint libraries", "precision workshops", "quality control stations"]
            },
            "retail": {
                "name": "The Trade Pact",
                "symbol": "woven basket and ink-stamped receipt",
                "colors": "market greens, receipt whites, coin golds",
                "environment": "mercantile guild hall packed with trade goods",
                "packages": ["SIR"],
                "district_name": "Market Square",
                "levels": {
                    "cert1": {"name": "Market Stalls", "desc": "outer market stalls with basic retail and customer service training"},
                    "cert2": {"name": "Shop Fronts", "desc": "established shop fronts with sales techniques and inventory management"},
                    "cert3": {"name": "Trade Halls", "desc": "trade halls with advanced retail operations and team leadership"},
                    "cert4": {"name": "Commerce Center", "desc": "grand commerce center with retail business mastery and strategic planning"}
                },
                "buildings": ["product displays", "checkout counters", "storage warehouses", "customer service desks", "trade ledgers"]
            },
            "transport": {
                "name": "The Pathfinder Union",
                "symbol": "golden compass and swift wheels",
                "colors": "navigation blues, path browns, compass golds",
                "environment": "dockside guild managing goods across lands",
                "packages": ["TLI"],
                "district_name": "Dockside Hub",
                "levels": {
                    "cert1": {"name": "Loading Docks", "desc": "basic loading docks with fundamental transport and safety training"},
                    "cert2": {"name": "Logistics Center", "desc": "logistics center with supply chain and coordination management"},
                    "cert3": {"name": "Operations Hub", "desc": "operations hub with advanced transport planning and fleet management"},
                    "cert4": {"name": "Master's Port", "desc": "master's port with transport industry leadership and strategic logistics"}
                },
                "buildings": ["cargo warehouses", "dispatch offices", "vehicle maintenance bays", "route planning centers", "communication towers"]
            },
            "agriculture": {
                "name": "The Verdant Circle",
                "symbol": "sprouting leaf and soil rune",
                "colors": "nature greens, earth browns, growth yellows",
                "environment": "secluded forest retreat where apprentices cultivate wisdom",
                "packages": ["AHC"],
                "district_name": "Verdant Circle",
                "levels": {
                    "cert1": {"name": "Crop Fields", "desc": "outer crop fields with fundamental farming technique gardens"},
                    "cert2": {"name": "Greenhouses", "desc": "inner greenhouses with sustainable agriculture training complexes"},
                    "cert3": {"name": "Guildhouses", "desc": "farming guildhouses with advanced horticulture and land management"},
                    "cert4": {"name": "Grove Monastery", "desc": "sacred grove monastery with leadership in conservation and agricultural mastery"}
                },
                "buildings": ["gardening chambers", "irrigation temples", "natural learning shrines", "seed libraries", "harvest halls"]
            },
            "safety": {
                "name": "The Guardian Order",
                "symbol": "glowing shield and justice emblem",
                "colors": "guardian blues, shield silvers, justice golds",
                "environment": "fortress citadel with tactical training grounds",
                "packages": ["POL", "PUA"],
                "district_name": "Guardian Citadel",
                "levels": {
                    "cert1": {"name": "Training Fields", "desc": "outer training fields with fundamental public safety course obstacles"},
                    "cert2": {"name": "Police Stations", "desc": "police stations with security mastery and law enforcement training"},
                    "cert3": {"name": "Defensive Strongholds", "desc": "defensive strongholds with emergency response leadership command centers"},
                    "cert4": {"name": "Guardian Fortress", "desc": "grand guardian fortress with mastery in governance and protection leadership"}
                },
                "buildings": ["tactical war chambers", "command halls", "defense academies", "watchtowers", "training obstacle courses"]
            },
            "creative": {
                "name": "The Dreamweavers",
                "symbol": "paintbrush and theatrical mask",
                "colors": "artistic purples, creative oranges, inspiration golds",
                "environment": "floating theater pavilion where stories come alive",
                "packages": ["CUA"],
                "district_name": "Creative Pavilion",
                "levels": {
                    "cert1": {"name": "Art Studios", "desc": "ground-level art studios with fundamental creative technique workshops"},
                    "cert2": {"name": "Performance Halls", "desc": "performance halls with intermediate arts and cultural practice spaces"},
                    "cert3": {"name": "Master's Gallery", "desc": "master's gallery with advanced creative projects and exhibition spaces"},
                    "cert4": {"name": "Grand Theater", "desc": "floating grand theater with creative arts mastery and cultural leadership"}
                },
                "buildings": ["easel workshops", "stage platforms", "costume chambers", "music practice rooms", "exhibition galleries"]
            }
        }

    def generate_banner_prompts(self) -> List[AssetPrompt]:
        """Generate banner/header image prompts"""
        prompts = []
        
        # Main site banner
        prompts.append(AssetPrompt(
            category="Banners",
            asset_type="Main Header",
            name="Site Main Banner",
            prompt=f"{self.base_style}, panoramic fantasy landscape banner, "
                   f"multiple guild districts visible in distance, floating islands, "
                   f"magical academy atmosphere, welcoming adventure feeling, cinematic composition",
            negative_prompt=self.negative_prompts,
            dimensions="1920x400",
            style_notes="Wide cinematic banner showing the magical world overview"
        ))
        
        # Guild-specific banners
        for guild_key, guild in self.guilds.items():
            prompts.append(AssetPrompt(
                category="Banners",
                asset_type="Guild Banner",
                name=f"{guild['name']} Banner",
                prompt=f"{self.base_style}, banner design featuring {guild['environment']}, "
                       f"dominant colors: {guild['colors']}, {guild['symbol']} prominently featured, "
                       f"welcoming educational atmosphere, fantasy RPG aesthetic",
                negative_prompt=self.negative_prompts,
                dimensions="1200x300", 
                style_notes=f"Banner for {guild['name']} guild pages"
            ))
            
        return prompts

    def generate_background_prompts(self) -> List[AssetPrompt]:
        """Generate background image prompts"""
        prompts = []
        
        # Main backgrounds
        bg_types = [
            ("General", "mystical academy grounds with floating elements"),
            ("Dashboard", "cozy study room with magical books and scrolls"),
            ("Profile", "personal adventure tent with equipment and maps"),
            ("Lessons", "classroom in magical tower with floating text elements")
        ]
        
        for bg_name, bg_desc in bg_types:
            prompts.append(AssetPrompt(
                category="Backgrounds",
                asset_type="Page Background",
                name=f"{bg_name} Background",
                prompt=f"{self.base_style}, {bg_desc}, subtle pattern suitable for text overlay, "
                       f"warm atmospheric lighting, detailed but not distracting, fantasy environment",
                negative_prompt=f"{self.negative_prompts}, busy composition, high contrast patterns",
                dimensions="1920x1080",
                style_notes=f"Background for {bg_name.lower()} pages, needs to support text readability"
            ))
            
        return prompts

    def generate_guild_icon_prompts(self) -> List[AssetPrompt]:
        """Generate guild icon prompts"""
        prompts = []
        
        for guild_key, guild in self.guilds.items():
            # Main guild icon
            prompts.append(AssetPrompt(
                category="Icons",
                asset_type="Guild Icon",
                name=f"{guild['name']} Icon",
                prompt=f"{self.base_style}, guild emblem design, {guild['symbol']}, "
                       f"colors: {guild['colors']}, circular badge format, detailed symbol, "
                       f"professional guild crest, magical runes around border",
                negative_prompt=f"{self.negative_prompts}, text, letters, words",
                dimensions="512x512",
                style_notes=f"Main icon for {guild['name']}"
            ))
            
            # Small navigation icon version
            prompts.append(AssetPrompt(
                category="Icons", 
                asset_type="Nav Icon",
                name=f"{guild['name']} Nav Icon",
                prompt=f"{self.base_style}, simplified guild symbol, {guild['symbol']}, "
                       f"clean minimal design, {guild['colors']}, icon suitable for small sizes",
                negative_prompt=f"{self.negative_prompts}, complex details, text",
                dimensions="128x128",
                style_notes=f"Small navigation icon for {guild['name']}"
            ))
            
        return prompts

    def generate_ui_element_prompts(self) -> List[AssetPrompt]:
        """Generate UI element prompts"""
        prompts = []
        
        ui_elements = [
            ("Progress Bar Empty", "empty magical progress bar with ornate borders", "800x60"),
            ("Progress Bar Fill", "glowing magical energy fill for progress bar", "800x60"),
            ("Button Normal", "fantasy parchment button with soft glow", "200x60"),
            ("Button Hover", "fantasy parchment button with bright magical glow", "200x60"),
            ("Card Background", "scroll parchment with soft shadow for content cards", "400x300"),
            ("Achievement Badge", "golden achievement medal with ribbon", "200x200"),
            ("XP Crystal", "glowing experience crystal gem", "100x100"),
            ("Level Star", "magical five-pointed star for level indicators", "80x80")
        ]
        
        for element_name, element_desc, dimensions in ui_elements:
            prompts.append(AssetPrompt(
                category="UI Elements",
                asset_type=element_name,
                name=element_name,
                prompt=f"{self.base_style}, {element_desc}, game UI asset, "
                       f"transparent background compatible, soft magical glow",
                negative_prompt=f"{self.negative_prompts}, harsh edges, modern UI",
                dimensions=dimensions,
                style_notes=f"UI component: {element_name}"
            ))
            
        return prompts

    def generate_character_prompts(self) -> List[AssetPrompt]:
        """Generate character/avatar prompts"""
        prompts = []
        
        # Generic avatars
        avatar_types = [
            ("Male Student", "young male apprentice in adventure gear"),
            ("Female Student", "young female apprentice in adventure gear"), 
            ("Non-binary Student", "young apprentice in adventure gear, androgynous features"),
            ("Guild Master", "wise elderly guild leader with ornate robes"),
            ("Mentor", "friendly middle-aged instructor with teaching materials")
        ]
        
        for avatar_name, avatar_desc in avatar_types:
            prompts.append(AssetPrompt(
                category="Characters",
                asset_type="Avatar",
                name=f"{avatar_name} Avatar",
                prompt=f"{self.base_style}, {avatar_desc}, expressive eyes, "
                       f"friendly welcoming expression, three-quarter view, "
                       f"detailed clothing and accessories, magical atmosphere",
                negative_prompt=f"{self.negative_prompts}, aggressive expression, hyper-anime style",
                dimensions="512x512",
                style_notes=f"Character avatar: {avatar_name}"
            ))
            
        return prompts

    def generate_level_progression_prompts(self) -> List[AssetPrompt]:
        """Generate certification level progression assets"""
        prompts = []
        
        for guild_key, guild in self.guilds.items():
            for level_key, level_info in guild['levels'].items():
                # Level environment background
                prompts.append(AssetPrompt(
                    category="Level Backgrounds",
                    asset_type="Certification Level",
                    name=f"{guild['name']} - {level_info['name']}",
                    prompt=f"{self.base_style}, {level_info['desc']}, "
                           f"colors: {guild['colors']}, atmospheric {guild['district_name']} setting, "
                           f"progressive difficulty visualization, {level_key.upper()} certification level",
                    negative_prompt=self.negative_prompts,
                    dimensions="1200x600",
                    style_notes=f"{level_key.upper()} level for {guild['name']}"
                ))
                
                # Level progress indicator
                prompts.append(AssetPrompt(
                    category="Level Indicators",
                    asset_type="Progress Icon",
                    name=f"{level_key.upper()} Badge - {guild['name']}",
                    prompt=f"{self.base_style}, certification badge design, "
                           f"{guild['symbol']}, {level_key.upper()} Roman numeral, "
                           f"colors: {guild['colors']}, guild emblem style",
                    negative_prompt=f"{self.negative_prompts}, text, letters",
                    dimensions="200x200",
                    style_notes=f"Progress badge for {level_key.upper()} certification"
                ))
                
        return prompts

    def generate_building_asset_prompts(self) -> List[AssetPrompt]:
        """Generate individual building and location assets"""
        prompts = []
        
        for guild_key, guild in self.guilds.items():
            for building in guild['buildings']:
                # Interior room/building view
                prompts.append(AssetPrompt(
                    category="Buildings",
                    asset_type="Interior",
                    name=f"{guild['name']} - {building.title()}",
                    prompt=f"{self.base_style}, interior view of {building}, "
                           f"{guild['district_name']} architectural style, "
                           f"colors: {guild['colors']}, educational learning environment, "
                           f"functional workspace with magical atmosphere",
                    negative_prompt=self.negative_prompts,
                    dimensions="800x600",
                    style_notes=f"Interior of {building} in {guild['district_name']}"
                ))
                
                # Building icon for navigation
                prompts.append(AssetPrompt(
                    category="Building Icons",
                    asset_type="Location Icon", 
                    name=f"{building.title()} Icon",
                    prompt=f"{self.base_style}, simplified icon of {building}, "
                           f"miniature building representation, isometric style, "
                           f"colors: {guild['colors']}, clear recognizable shape",
                    negative_prompt=f"{self.negative_prompts}, complex details, text",
                    dimensions="128x128",
                    style_notes=f"Navigation icon for {building}"
                ))
                
        return prompts

    def generate_district_map_prompts(self) -> List[AssetPrompt]:
        """Generate district overview maps"""
        prompts = []
        
        for guild_key, guild in self.guilds.items():
            # District overview map
            prompts.append(AssetPrompt(
                category="District Maps",
                asset_type="Overview Map",
                name=f"{guild['district_name']} Map",
                prompt=f"{self.base_style}, bird's eye view map of {guild['district_name']}, "
                       f"showing {guild['environment']}, certification level progression paths, "
                       f"colors: {guild['colors']}, fantasy map aesthetic with landmarks, "
                       f"RPG game map style with clear navigation routes",
                negative_prompt=f"{self.negative_prompts}, modern UI elements, realistic photography",
                dimensions="1024x1024",
                style_notes=f"Interactive map for {guild['district_name']} navigation"
            ))
            
            # District entrance gate
            prompts.append(AssetPrompt(
                category="District Gates",
                asset_type="Entrance",
                name=f"{guild['district_name']} Gate",
                prompt=f"{self.base_style}, grand entrance gate to {guild['district_name']}, "
                       f"featuring {guild['symbol']}, {guild['colors']}, "
                       f"welcoming archway with guild banners, magical portal effect, "
                       f"impressive architecture matching district theme",
                negative_prompt=self.negative_prompts,
                dimensions="600x800",
                style_notes=f"Main entrance to {guild['district_name']}"
            ))
            
        return prompts

    def generate_npc_character_prompts(self) -> List[AssetPrompt]:
        """Generate NPC characters for each guild"""
        prompts = []
        
        npc_types = [
            ("Guild Leader", "wise experienced leader with ornate robes"),
            ("Instructor", "friendly mentor with teaching materials"),
            ("Student Guide", "helpful peer student with welcoming expression"),
            ("Shopkeeper", "cheerful vendor managing learning resources")
        ]
        
        for guild_key, guild in self.guilds.items():
            for npc_type, npc_desc in npc_types:
                prompts.append(AssetPrompt(
                    category="NPCs",
                    asset_type=npc_type,
                    name=f"{guild['name']} {npc_type}",
                    prompt=f"{self.base_style}, {npc_desc}, "
                           f"themed for {guild['district_name']}, colors: {guild['colors']}, "
                           f"expressive friendly face, three-quarter view, "
                           f"clothing and accessories matching guild aesthetic",
                    negative_prompt=f"{self.negative_prompts}, aggressive expression, modern clothing",
                    dimensions="400x600",
                    style_notes=f"{npc_type} character for {guild['name']}"
                ))
                
        return prompts

    def generate_certification_rewards_prompts(self) -> List[AssetPrompt]:
        """Generate certification completion rewards"""
        prompts = []
        
        reward_types = [
            ("Certificate", "ornate parchment certificate with wax seal"),
            ("Medal", "achievement medal with ribbon"),
            ("Trophy", "small decorative trophy"),
            ("Badge", "embroidered skill badge")
        ]
        
        for guild_key, guild in self.guilds.items():
            for level_key, level_info in guild['levels'].items():
                for reward_name, reward_desc in reward_types:
                    prompts.append(AssetPrompt(
                        category="Rewards",
                        asset_type=reward_name,
                        name=f"{level_key.upper()} {reward_name} - {guild['name']}",
                        prompt=f"{self.base_style}, {reward_desc}, "
                               f"featuring {guild['symbol']}, colors: {guild['colors']}, "
                               f"{level_key.upper()} certification level indicator, "
                               f"magical glow effect, high quality craftsmanship",
                        negative_prompt=f"{self.negative_prompts}, modern design, text",
                        dimensions="300x300",
                        style_notes=f"{reward_name} for completing {level_key.upper()} in {guild['name']}"
                    ))
                    
        return prompts
        """Generate bullet point and list element prompts"""
        prompts = []
        
        bullet_types = [
            ("Leaf Bullet", "small magical leaf", "For nature/growth content"),
            ("Star Bullet", "tiny glowing star", "For achievements/highlights"),
            ("Gem Bullet", "small crystal gem", "For valuable information"),
            ("Scroll Bullet", "miniature scroll", "For text-heavy content"),
            ("Feather Bullet", "magical feather quill", "For creative content")
        ]
        
        for bullet_name, bullet_desc, usage in bullet_types:
            prompts.append(AssetPrompt(
                category="UI Elements",
                asset_type="Bullet Point",
                name=bullet_name,
                prompt=f"{self.base_style}, {bullet_desc}, tiny detailed icon, "
                       f"soft magical glow, suitable for text lists",
                negative_prompt=f"{self.negative_prompts}, large size, complex details",
                dimensions="32x32",
                style_notes=f"Bullet point icon - {usage}"
            ))
            
        return prompts

    def generate_all_prompts(self) -> List[AssetPrompt]:
        """Generate all asset prompts"""
        all_prompts = []
        all_prompts.extend(self.generate_banner_prompts())
        all_prompts.extend(self.generate_background_prompts())
        all_prompts.extend(self.generate_guild_icon_prompts())
        all_prompts.extend(self.generate_ui_element_prompts())
        all_prompts.extend(self.generate_character_prompts())
        all_prompts.extend(self.generate_bullet_point_prompts())
        return all_prompts

    def export_to_json(self, filename: str = "ghibli_rpg_prompts.json"):
        """Export all prompts to JSON file"""
        prompts = self.generate_all_prompts()
        data = [asdict(prompt) for prompt in prompts]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(prompts)} prompts to {filename}")

    def export_to_csv(self, filename: str = "ghibli_rpg_prompts.csv"):
        """Export all prompts to CSV file"""
        prompts = self.generate_all_prompts()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Category', 'Asset Type', 'Name', 'Prompt', 'Negative Prompt', 'Dimensions', 'Style Notes'])
            
            for prompt in prompts:
                writer.writerow([
                    prompt.category,
                    prompt.asset_type, 
                    prompt.name,
                    prompt.prompt,
                    prompt.negative_prompt,
                    prompt.dimensions,
                    prompt.style_notes
                ])
        
        print(f"Exported {len(prompts)} prompts to {filename}")

    def get_api_ready_prompts(self) -> Dict[str, List[Dict]]:
        """Get prompts formatted for API calls"""
        prompts = self.generate_all_prompts()
        
        api_prompts = {}
        for prompt in prompts:
            category = prompt.category
            if category not in api_prompts:
                api_prompts[category] = []
                
            api_prompts[category].append({
                'name': prompt.name,
                'prompt': prompt.prompt,
                'negative_prompt': prompt.negative_prompt,
                'width': int(prompt.dimensions.split('x')[0]),
                'height': int(prompt.dimensions.split('x')[1]),
                'style_notes': prompt.style_notes
            })
            
        return api_prompts

    def print_summary(self):
        """Print a summary of all generated prompts"""
        prompts = self.generate_all_prompts()
        
        categories = {}
        for prompt in prompts:
            if prompt.category not in categories:
                categories[prompt.category] = 0
            categories[prompt.category] += 1
            
        print("=== GHIBLI RPG ASSET GENERATOR SUMMARY ===")
        print(f"Total prompts generated: {len(prompts)}")
        print("\nBreakdown by category:")
        for category, count in categories.items():
            print(f"  {category}: {count} assets")
            
        print(f"\nGuilds covered: {len(self.guilds)}")
        for guild_key, guild in self.guilds.items():
            packages = ", ".join(guild['packages'])
            print(f"  - {guild['name']} ({packages})")

# Example usage and API integration helper functions
def generate_with_openai_dalle(prompt_data: Dict, api_key: str):
    """Example function for OpenAI DALL-E API integration"""
    import openai
    
    # This is pseudocode - adjust based on actual API
    openai.api_key = api_key
    
    try:
        response = openai.Image.create(
            prompt=prompt_data['prompt'],
            n=1,
            size=f"{prompt_data['width']}x{prompt_data['height']}"
        )
        return response['data'][0]['url']
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def generate_with_midjourney_api(prompt_data: Dict, api_key: str):
    """Example function for Midjourney API integration"""
    # This would depend on the specific Midjourney API implementation
    # Currently placeholder as Midjourney doesn't have a public API
    pass

def generate_with_stability_ai(prompt_data: Dict, api_key: str):
    """Example function for Stability AI API integration"""
    import requests
    
    # Pseudocode for Stability AI API
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    data = {
        "text_prompts": [
            {"text": prompt_data['prompt']},
            {"text": prompt_data['negative_prompt'], "weight": -1}
        ],
        "cfg_scale": 7,
        "height": prompt_data['height'],
        "width": prompt_data['width'],
        "samples": 1,
        "steps": 30,
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

if __name__ == "__main__":
    # Initialize the generator
    generator = GhibliRPGAssetGenerator()
    
    # Print summary
    generator.print_summary()
    
    # Export to files
    generator.export_to_json()
    generator.export_to_csv()
    
    # Get API-ready prompts
    api_prompts = generator.get_api_ready_prompts()
    
    print(f"\n=== SAMPLE PROMPTS ===")
    print("Banner example:")
    sample_banner = api_prompts['Banners'][0]
    print(f"Name: {sample_banner['name']}")
    print(f"Prompt: {sample_banner['prompt'][:100]}...")
    
    print(f"\nIcon example:")
    sample_icon = api_prompts['Icons'][0] 
    print(f"Name: {sample_icon['name']}")
    print(f"Prompt: {sample_icon['prompt'][:100]}...")
    
    print("\n=== READY FOR API INTEGRATION ===")
    print("Use the exported JSON/CSV files or api_prompts dictionary")
    print("with your preferred AI image generation service!")
