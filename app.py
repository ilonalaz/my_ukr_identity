from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import anthropic
import json
import random

# Load environment variables
load_dotenv()

# Configure Flask to use current directory for templates and static files
app = Flask(__name__, 
            template_folder='.', 
            static_folder='.')
CORS(app)

# Initialize Anthropic client with error handling
try:
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Warning: ANTHROPIC_API_KEY not found in environment variables")
        client = None
    else:
        client = anthropic.Anthropic(api_key=api_key)
        print("Anthropic client initialized successfully")
except Exception as e:
    print(f"Error initializing Anthropic client: {e}")
    client = None

# Cultural data for AI responses
CULTURAL_REGIONS = {
    'київ': 'Київ - мати міст руських - живе у вашому серці. Ви з столиці, що тисячу років була центром української духовності.',
    'львів': 'Львівська земля наділила вас духом свободи та культурної гордості. Ви з міста лева, де кожен камінь дихає історією.',
    'харків': 'Харківщина дала вам силу інтелекту та стійкості. Ви з краю, що подарував світу багато геніїв.',
    'одеса': 'Одеський гумор та життєлюбність - це частина вашої душі. Море вольності тече у ваших венах.',
    'дніпро': 'Дніпро-батько благословив вас силою та незламністю. Ви з краю, де ковалася українська незалежність.',
    'полтава': 'Полтавщина наділила вас мелодійністю мови та мудрістю землі. Ви з краю Гоголя та народних пісень.',
    'галичина': 'Галицька земля - це ваша духовна батьківщина. Кожна гора Карпат пам\'ятає ваші корені.',
    'волинь': 'Волинська земля дала вам силу духу та вірність традиціям. Ви з краю древніх лісів та чистих джерел.',
    'закарпаття': 'Карпатські вершини навчили вас стійкості та гордості. Ви з краю, де небо торкається землі.',
    'чернігів': 'Чернігівщина наділила вас мудрістю віків та спокійною силою. Ви з краю древніх курганів.'
}

WISDOM_QUOTES = [
    "\"Україна - це не просто країна, це стан душі\" - Тарас Шевченко",
    "\"Борітеся - поборете, вам Бог помагає!\" - Тарас Шевченко", 
    "\"Слово наше повинне бути правдою, а правда наша - силою\" - Іван Франко",
    "\"Любіть Україну, як сонце, любіть!\" - Володимир Сосюра",
    "\"Нам треба йти в народ, не щоб навчити його, а щоб навчитися від нього\" - Микола Костомаров",
    "\"Я не можу жити без України\" - Леся Українка",
    "\"Встань, Україно, встань і йди!\" - Павло Тичина"
]

def check_anthropic_client():
    """Check if Anthropic client is available"""
    if client is None:
        return False, "Anthropic API недоступний. Будь ласка, перевірте налаштування API ключа."
    return True, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files from the current directory"""
    from flask import send_from_directory
    return send_from_directory('.', filename)

@app.route('/api/reflect', methods=['POST'])
def generate_reflection():
    try:
        # Check if Anthropic client is available
        client_available, error_msg = check_anthropic_client()
        if not client_available:
            return jsonify({'error': error_msg, 'success': False}), 500
        
        data = request.json
        user_story = data.get('story', '')
        
        if not user_story:
            return jsonify({'error': 'Будь ласка, розкажіть про себе'}), 400
        
        # Create AI prompt for cultural reflection
        prompt = f"""
        Ти - мудрий наставник української культури та ідентичності. Користувач розповів свою особисту історію. 
        Твоє завдання - створити глибоке, емоційне відображення їхнього зв'язку з Україною.
        
        Історія користувача: "{user_story}"
        
        Створи персоналізовану відповідь (250-400 слів) ТІЛЬКИ УКРАЇНСЬКОЮ МОВОЮ, що включає:
        1. Теплий, емоційний тон
        2. Зв'язок з українською культурою, традиціями, історією
        3. Персональні деталі з їхньої історії
        4. Використання символів (соняшник 🌻, тризуб, калина, вишиванка)
        5. Підтвердження їхньої української ідентичності
        6. Натхнення та гордість
        
        Почни з "💙" і зроби відповідь душевною, особистою та надихаючою.
        """
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.8,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        reflection = message.content[0].text
        
        return jsonify({
            'reflection': reflection,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Помилка: {str(e)}',
            'success': False
        }), 500

@app.route('/api/lesson', methods=['POST'])
def get_lesson():
    try:
        # Check if Anthropic client is available
        client_available, error_msg = check_anthropic_client()
        if not client_available:
            return jsonify({'error': error_msg, 'success': False}), 500
        
        data = request.json
        lesson_type = data.get('type', '')
        user_level = data.get('level', 'початковий')
        
        lesson_prompts = {
            'language': f"""
            Створи урок української мови для {user_level} рівня. Включи:
            1. 5 красивих українських слів з поясненням
            2. 2-3 корисні фрази
            3. Українське прислів'я з поясненням
            4. Короткий вірш або пісню
            Використай емоційний підхід та культурний контекст. Тільки українською мовою.
            """,
            'history': f"""
            Розкажи захоплюючу історичну історію з української історії для {user_level} рівня:
            1. Виберіть цікавий період або особистість
            2. Розкажіть як захоплюючу розповідь
            3. Поясніть значення для сучасної України
            4. Додайте емоційний зв'язок
            Тільки українською мовою, 300-400 слів.
            """,
            'culture': f"""
            Поділися українською культурною традицією для {user_level} рівня:
            1. Виберіть свято, обряд або традицію
            2. Поясніть історію та значення
            3. Як це практикувати сьогодні
            4. Чому це важливо для ідентичності
            Тільки українською мовою, з емоційним підходом.
            """,
            'folklore': f"""
            Розказжи українську народну казку або легенду для {user_level} рівня:
            1. Виберіть менш відому, але цікаву історію
            2. Розкажіть живо та захоплююче
            3. Поясніть мораль та культурне значення
            4. Зв'яжіть з сучасним життям
            Тільки українською мовою.
            """
        }
        
        prompt = lesson_prompts.get(lesson_type, lesson_prompts['language'])
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.8,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        lesson_content = message.content[0].text
        
        return jsonify({
            'lesson': lesson_content,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Помилка: {str(e)}',
            'success': False
        }), 500

@app.route('/api/advanced-lesson', methods=['POST'])
def get_advanced_lesson():
    try:
        # Check if Anthropic client is available
        client_available, error_msg = check_anthropic_client()
        if not client_available:
            return jsonify({'error': error_msg, 'success': False}), 500
        
        data = request.json
        category = data.get('category', '')
        subcategory = data.get('subcategory', '')
        subcategory_name = data.get('subcategoryName', '')
        
        # Advanced intellectual prompts for Ukrainian content - well formatted and informative
        advanced_prompts = {
            'language': {
                'etymology': """
                Розкажи про одне цікаве українське слово, його походження та культурне значення.
                Структуруй відповідь з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'dialects': """
                Поділися цікавою особливістю українського діалекту або говірки.
                Включи назву регіону, приклади слів та їх значення.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'language_culture_code': """
                Покажи на прикладі, як українська мова відображає наш світогляд.
                Обери вираз або поняття, що розкриває українську ментальність.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'neologisms_archaisms': """
                Розкажи про нове або старе українське слово та його значення.
                Поясни його походження та використання.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'psycholinguistics': """
                Поділися фактом про те, як українська мова впливає на наше мислення.
                Покажи зв'язок мови та свідомості на конкретному прикладі.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'linguistics_random': """
                Розкажи про цікаву лінгвістичну особливість української мови.
                Обери те, що здивує і надихне вивчати мову глибше.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """
            },
            'history': {
                'kyivan_rus': """
                Розкажи про важливу подію або постать Київської Русі.
                Включи дати, історичний контекст та значення для сучасної України.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                200-250 слів, тільки українською мовою.
                """,
                'cossack_state': """
                Поділися цікавою історією з часів козацької держави.
                Включи історичні факти, постаті та їх вплив на українську ідентичність.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                200-250 слів, тільки українською мовою.
                """,
                'galicia_volhynia': """
                Розкажи про важливу подію Галицько-Волинського князівства.
                Покажи європейські зв'язки, культурні досягнення та історичне значення.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                200-250 слів, тільки українською мовою.
                """,
                'unr_liberation': """
                Поділися яскравою історією визвольних змагань 1917-1921.
                Включи ключові події, постаті та їх значення для української державності.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                200-250 слів, тільки українською мовою.
                """,
                'holodomor_repressions': """
                Розкажи про конкретну історію пам'яті про Голодомор.
                Покажи важливість збереження історичної правди та пам'яті.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                200-250 слів, тільки українською мовою.
                """,
                'history_random': """
                Поділися захоплюючою історією з українського минулого.
                Обери те, що надихає та показує силу українського духу.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                200-250 слів, тільки українською мовою.
                """
            },
            'ethnography': {
                'calendar_rituals': """
                Розкажи про українське свято або обряд та його значення.
                Включи історію, традиції та сучасне відзначення.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'folk_beliefs': """
                Поділися цікавою українською легендою або віруванням.
                Покажи мудрість предків та зв'язок з природою і традиціями.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'traditional_economy': """
                Розкажи про традиційне українське ремесло або заняття.
                Покажи майстерність, техніки та зв'язок з землею і культурою.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'family_traditions': """
                Поділися українською родинною традицією.
                Покажи, як це зміцнює сім'ю, передає цінності та зберігає культуру.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'oral_folklore': """
                Розкажи українську народну казку або приказку.
                Покажи мудрість, гумор та життєві уроки нашого народу.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'ethnography_random': """
                Поділися цікавою українською традицією.
                Обери те, що показує красу та унікальність нашої культури.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """
            },
            'literature': {
                'romanticism_shevchenko': """
                Поділися улюбленим віршем або рядком Тараса Шевченка.
                Включи контекст написання та вплив на українську літературу.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'realism_19th': """
                Розкажи про твір українського реалізму XIX століття.
                Покажи, як література відображала життя народу та соціальні проблеми.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'modernism_1920s': """
                Поділися фактом про "розстріляне відродження" 1920-х.
                Покажи талант, новаторство та трагічну долю того покоління.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'sixtiers_dissidents': """
                Розкажи про одного з шістдесятників та його внесок.
                Покажи мужність, творчість та відданість українській справі.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'contemporary_literature': """
                Поділися сучасним українським твором або автором.
                Покажи, як література розвивається та відображає сучасні реалії.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """,
                'literature_random': """
                Розкажи про цікаву постать української літератури.
                Обери те, що надихне читати більше та пишатися спадщиною.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                150-200 слів, тільки українською мовою.
                """
            },
            'freedom': {
                'cossack_uprisings': """
                Розкажи про козацького героя та його подвиг.
                Включи історичний контекст, дії та вплив на українську боротьбу за свободу.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                200-250 слів, тільки українською мовою.
                """,
                'liberation_1917_1921': """
                Поділися героїчною історією визвольних змагань.
                Покажи жертовність, боротьбу та прагнення до незалежності.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                200-250 слів, тільки українською мовою.
                """,
                'oun_upa': """
                Розкажи про акт опору або героїзму ОУН-УПА.
                Покажи незламність духу борців за волю та їх жертви.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                200-250 слів, тільки українською мовою.
                """,
                'dissident_movement': """
                Поділися історією українського дисидента.
                Покажи мужність боротьби за правду та права людини.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                200-250 слів, тільки українською мовою.
                """,
                'revolution_dignity': """
                Розкажи про яскравий момент Революції Гідності.
                Покажи силу об'єднаного народу та прагнення до змін.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                200-250 слів, тільки українською мовою.
                """,
                'freedom_random': """
                Поділися історією українського героїзму.
                Обери те, що надихає на боротьбу за свободу та гідність.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                200-250 слів, тільки українською мовою.
                """
            },
            'content': {
                'classic_songs': """
                🎵 Розкажи про класичну українську пісню та її історію.
                Включи автора, рік створення, контекст та вплив на культуру.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                ВАЖЛИВО: Завершуй відповідь повністю, не обривай речення посередині.
                150-200 слів, тільки українською мовою.
                """,
                'modern_music': """
                🎤 Поділися сучасною українською піснею та її значенням.
                Покажи, як музика об'єднує покоління та популяризує українську культуру.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                ВАЖЛИВО: Завершуй відповідь повністю, не обривай речення посередині.
                150-200 слів, тільки українською мовою.
                """,
                'iconic_books': """
                📚 Розкажи про знакову українську книгу.
                Покажи її значення, вплив на суспільство та чому варто прочитати.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                ВАЖЛИВО: Завершуй відповідь повністю, не обривай речення посередині.
                150-200 слів, тільки українською мовою.
                """,
                'cinema_theater': """
                🎬 Поділися українським фільмом або виставою.
                Покажи, як візуальне мистецтво розповідає нашу історію та культуру.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                ВАЖЛИВО: Завершуй відповідь повністю, не обривай речення посередині.
                150-200 слів, тільки українською мовою.
                """,
                'folk_songs': """
                🎭 Розкажи про українську народну пісню або коляду.
                Покажи її красу, історію та зв'язок з традиціями і обрядами.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                ВАЖЛИВО: Завершуй відповідь повністю, не обривай речення посередині.
                150-200 слів, тільки українською мовою.
                """,
                'content_random': """
                Поділися цікавим фактом про український контент.
                Обери те, що показує багатство та різноманітність нашої культури.
                Структуруй з заголовком і абзацами. Використовуй HTML теги: <b>для жирного тексту</b> та <p>для абзаців</p>.
                ВАЖЛИВО: Завершуй відповідь повністю, не обривай речення посередині.
                150-200 слів, тільки українською мовою.
                """
            }
        }
        
        # Get the appropriate prompt
        category_prompts = advanced_prompts.get(category, {})
        prompt = category_prompts.get(subcategory, f"""
        Створи інтелектуальний матеріал на тему "{subcategory_name}" у категорії "{category}".
        Розкрий тему глибоко, академічно, з аналізом та сучасною актуальністю.
        400-500 слів, тільки українською мовою.
        """)
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.8,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        lesson_content = message.content[0].text
        
        return jsonify({
            'lesson': lesson_content,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Помилка: {str(e)}',
            'success': False
        }), 500

@app.route('/api/daily-wisdom')
def get_daily_wisdom():
    try:
        # Check if Anthropic client is available
        client_available, error_msg = check_anthropic_client()
        if not client_available:
            # Fallback to static quotes if API is not available
            fallback_wisdom = random.choice(WISDOM_QUOTES)
            return jsonify({
                'wisdom': fallback_wisdom,
                'success': True
            })
        
        # Use AI to generate personalized daily wisdom
        prompt = """
        Створи надихаючу українську мудрість дня. Це може бути:
        1. Цитата українського письменника/поета
        2. Народна мудрість або прислів'я
        3. Сучасна мотивація в українському дусі
        
        Зроби це коротко (1-2 речення), надихаюче та автентично українським.
        Тільки українською мовою.
        """
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.8,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        wisdom = message.content[0].text
        
        return jsonify({
            'wisdom': wisdom,
            'success': True
        })
        
    except Exception as e:
        # Fallback to static quotes
        fallback_wisdom = random.choice(WISDOM_QUOTES)
        return jsonify({
            'wisdom': fallback_wisdom,
            'success': True
        })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Check if Anthropic client is available
        client_available, error_msg = check_anthropic_client()
        if not client_available:
            return jsonify({'error': error_msg, 'success': False}), 500
        
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Повідомлення не може бути порожнім'}), 400
        
        # Create AI prompt for general chat
        prompt = f"""
        Ти - мудрий український наставник та друг. Користувач написав: "{user_message}"
        
        Відповідай як досвідчений українець, що:
        1. Розуміє українську культуру та історію
        2. Може дати мудрі поради
        3. Підтримує українську ідентичність
        4. Говорить тільки українською мовою
        5. Використовує емоційний, теплий тон
        6. При потребі включає культурні референси
        
        ВАЖЛИВО: Завершуй відповідь повністю, не обривай речення посередині.
        Тримай відповідь в межах 150-250 слів, але завжди закінчуй думку.
        """
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.8,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response = message.content[0].text
        print(f"Chat response length: {len(response)}")
        print(f"Chat response ends with: {response[-50:]}")
        
        return jsonify({
            'response': response,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Помилка: {str(e)}',
            'success': False
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
