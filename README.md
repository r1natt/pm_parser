<h1 align="center">PM Parser</h1>

<div align="center">
	
  <img width="100" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/python.png" alt="Python" title="Python"/>
	<img width="100" src="https://www.gstatic.com/images/branding/product/2x/google_cloud_64dp.png" alt="Google API" title="Google API"/>
	<img width="100" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/postgresql.png" alt="PostgreSQL" title="PostgreSQL"/>
	<img width="100" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/postman.png" alt="Postman" title="Postman"/>
  
</div>

---

**Данный проект является фриланс заказом и выложен с разрешения заказчика.**

# Задача

Парсить сайт букмекера с целью составления динамики коэффициентов за определенные промежутки времени до начала самого матча: за 2 дня, за 1 день, за 3 часа, за 50 минут, за 5 минут до начала матча.


# Принцип работы

<i>Загрузка сайта букмекера занимает от 15 до 30 секунд, поэтому был использован не простой парсер, а запросы по тем запросам, который использует сам сайт для загрузки матчей. </i>

Принцип работы такой:
1) Инициализируется класс Cycle, создающий 2 таймера:
   * на каждые 10 секунд для идущих матчей
   * на каждые 5 минут для всех матчей
2) При отрабатывании одного из таймеров запускается соответствующая функция запросов из класса Actions
   Класс Actions - является сборником функций, которые выполняются запросы из класса InnerAPI (reqs.py)
3) Все ответы обрабатываются и сохраняются в БД.
4) По окончанию выполнения запросов все строки выгружаются в два листа google таблиц:
   * Запланированные и live матчи
   * Окончившиеся матчи
