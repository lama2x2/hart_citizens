from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from kingdom.models import Kingdom, Test, Question, King, Citizen
from kingdom.utils import log_registration

User = get_user_model()


class Command(BaseCommand):
    help = 'Создание начальных данных для системы'

    def handle(self, *args, **options):
        self.stdout.write('Создание начальных данных...')
        
        # Создаем королевства
        kingdoms_data = [
            {
                'name': 'Королевство Северных Земель',
                'description': 'Суровое королевство на севере, известное своими воинами и магией льда.'
            },
            {
                'name': 'Королевство Золотых Равнин',
                'description': 'Богатое королевство с плодородными землями и развитой торговлей.'
            },
            {
                'name': 'Королевство Лесных Теней',
                'description': 'Таинственное королевство, скрытое в глубинах древних лесов.'
            },
            {
                'name': 'Королевство Горных Вершин',
                'description': 'Королевство в горах, известное своими мастерами и драгоценными камнями.'
            },
            {
                'name': 'Королевство Морских Волн',
                'description': 'Королевство на побережье, владеющее искусством мореплавания.'
            }
        ]
        
        kingdoms = []
        for kingdom_data in kingdoms_data:
            kingdom, created = Kingdom.objects.get_or_create(
                name=kingdom_data['name'],
                defaults={'description': kingdom_data['description']}
            )
            kingdoms.append(kingdom)
            if created:
                self.stdout.write(f'Создано королевство: {kingdom.name}')
        
        # Создаем тестовые испытания для каждого королевства
        test_questions = [
            {
                'text': 'Считаете ли вы, что честность является основой любого общества?',
                'correct_answer': True,
                'order': 1
            },
            {
                'text': 'Должен ли правитель всегда ставить интересы государства выше личных?',
                'correct_answer': True,
                'order': 2
            },
            {
                'text': 'Согласны ли вы, что война всегда является лучшим решением конфликтов?',
                'correct_answer': False,
                'order': 3
            },
            {
                'text': 'Должны ли подданные беспрекословно подчиняться всем приказам короля?',
                'correct_answer': False,
                'order': 4
            },
            {
                'text': 'Считаете ли вы, что образование должно быть доступно всем слоям общества?',
                'correct_answer': True,
                'order': 5
            },
            {
                'text': 'Должен ли король нести ответственность за благополучие всех своих подданных?',
                'correct_answer': True,
                'order': 6
            },
            {
                'text': 'Согласны ли вы, что богатство должно распределяться только среди знати?',
                'correct_answer': False,
                'order': 7
            },
            {
                'text': 'Должны ли законы применяться одинаково ко всем, независимо от социального статуса?',
                'correct_answer': True,
                'order': 8
            },
            {
                'text': 'Считаете ли вы, что магия должна быть запрещена в королевстве?',
                'correct_answer': False,
                'order': 9
            },
            {
                'text': 'Должен ли король консультироваться с советниками перед принятием важных решений?',
                'correct_answer': True,
                'order': 10
            }
        ]
        
        for kingdom in kingdoms:
            test, created = Test.objects.get_or_create(
                kingdom=kingdom,
                defaults={
                    'title': f'Тестовое испытание для {kingdom.name}',
                    'description': f'Испытание для определения достойных подданных королевства {kingdom.name}',
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Создан тест для королевства: {kingdom.name}')
                
                # Создаем вопросы для теста
                for question_data in test_questions:
                    Question.objects.create(
                        test=test,
                        text=question_data['text'],
                        correct_answer=question_data['correct_answer'],
                        order=question_data['order']
                    )
                
                self.stdout.write(f'Создано {len(test_questions)} вопросов для теста королевства {kingdom.name}')
        
        # Создаем демо-королей
        demo_kings = [
            {
                'username': 'king_north',
                'first_name': 'Эдрик',
                'last_name': 'Северный',
                'kingdom': kingdoms[0],
                'max_citizens': 3
            },
            {
                'username': 'king_golden',
                'first_name': 'Аурелиус',
                'last_name': 'Золотой',
                'kingdom': kingdoms[1],
                'max_citizens': 5
            },
            {
                'username': 'king_forest',
                'first_name': 'Сильван',
                'last_name': 'Лесной',
                'kingdom': kingdoms[2],
                'max_citizens': 4
            }
        ]
        
        for king_data in demo_kings:
            if not User.objects.filter(username=king_data['username']).exists():
                user = User.objects.create_user(
                    username=king_data['username'],
                    password='king123',
                    first_name=king_data['first_name'],
                    last_name=king_data['last_name'],
                    role='king',
                    is_active=True
                )
                
                king, created = King.objects.get_or_create(
                    user=user,
                    kingdom=king_data['kingdom'],
                    defaults={'max_citizens': king_data['max_citizens']}
                )
                
                if created:
                    self.stdout.write(f'Создан король: {user.get_full_name()} ({king_data["kingdom"].name})')
        
        # Создаем демо-подданных
        demo_citizens = [
            {
                'username': 'citizen_anna',
                'email': 'citizen1@example.com',
                'first_name': 'Анна',
                'last_name': 'Смелая',
                'kingdom': kingdoms[0],
                'age': 25,
                'pigeon_email': 'anna.pigeon@example.com'
            },
            {
                'username': 'citizen_boris',
                'email': 'citizen2@example.com',
                'first_name': 'Борис',
                'last_name': 'Мудрый',
                'kingdom': kingdoms[1],
                'age': 30,
                'pigeon_email': 'boris.pigeon@example.com'
            },
            {
                'username': 'citizen_victoria',
                'email': 'citizen3@example.com',
                'first_name': 'Виктория',
                'last_name': 'Быстрая',
                'kingdom': kingdoms[2],
                'age': 22,
                'pigeon_email': 'victoria.pigeon@example.com'
            },
            {
                'username': 'citizen_grigory',
                'email': 'citizen4@example.com',
                'first_name': 'Григорий',
                'last_name': 'Сильный',
                'kingdom': kingdoms[0],
                'age': 28,
                'pigeon_email': 'grigory.pigeon@example.com'
            },
            {
                'username': 'citizen_darya',
                'email': 'citizen5@example.com',
                'first_name': 'Дарья',
                'last_name': 'Красивая',
                'kingdom': kingdoms[1],
                'age': 26,
                'pigeon_email': 'darya.pigeon@example.com'
            }
        ]
        
        for citizen_data in demo_citizens:
            if not User.objects.filter(username=citizen_data['username']).exists():
                user = User.objects.create_user(
                    username=citizen_data['username'],
                    password='citizen123',
                    email=citizen_data['email'],
                    first_name=citizen_data['first_name'],
                    last_name=citizen_data['last_name'],
                    role='citizen',
                    is_active=True
                )
                
                citizen, created = Citizen.objects.get_or_create(
                    user=user,
                    kingdom=citizen_data['kingdom'],
                    defaults={
                        'age': citizen_data['age'],
                        'pigeon_email': citizen_data['pigeon_email']
                    }
                )
                
                if created:
                    self.stdout.write(f'Создан подданный: {user.get_full_name()} ({citizen_data["kingdom"].name})')
        
        # Создаем суперпользователя
        if not User.objects.filter(is_superuser=True).exists():
            superuser = User.objects.create_superuser(
                username='admin',
                password='admin123',
                first_name='Администратор',
                last_name='Системы',
                role='king'
            )
            self.stdout.write('Создан суперпользователь: admin (пароль: admin123)')
        
        self.stdout.write(
            self.style.SUCCESS('Начальные данные успешно созданы!')
        )
        self.stdout.write('\nДемо-аккаунты:')
        self.stdout.write('Короли:')
        self.stdout.write('  - king_north (пароль: king123)')
        self.stdout.write('  - king_golden (пароль: king123)')
        self.stdout.write('  - king_forest (пароль: king123)')
        self.stdout.write('\nПодданные:')
        self.stdout.write('  - citizen_anna (пароль: citizen123)')
        self.stdout.write('  - citizen_boris (пароль: citizen123)')
        self.stdout.write('  - citizen_victoria (пароль: citizen123)')
        self.stdout.write('  - citizen_grigory (пароль: citizen123)')
        self.stdout.write('  - citizen_darya (пароль: citizen123)')
        self.stdout.write('\nАдминистратор:')
        self.stdout.write('  - admin (пароль: admin123)')
