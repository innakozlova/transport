import pandas as pd
import os
from catboost import CatBoostRegressor

print("1. Загрузка данных по абсолютным путям...")

# Жесткий базовый путь к вашей папке dataset (взят из ваших скриншотов)
BASE_DIR = r"c:/Users/admi/Documents/school/AP1_Py_T02_ID_1375363-1/src/dataset"

# Собираем полные пути к файлам
train_path = os.path.join(BASE_DIR, "labels", "labels_train.csv")
test_path = os.path.join(BASE_DIR, "labels", "labels_test.csv")
validate_path = os.path.join(BASE_DIR, "validate", "points.csv")
sample_sub_path = os.path.join(BASE_DIR, "sample_submission.csv")
output_sub_path = os.path.join(BASE_DIR, "submission.csv")

# Читаем таблицы
train_data = pd.read_csv(train_path, sep=',')
test_data = pd.read_csv(test_path, sep=',')
validate_points = pd.read_csv(validate_path, sep=',')

print("2. Генерация продвинутых признаков (Парсинг даты)...")

# Исправленная функция: извлекаем час прямо из строки текста
def extract_time_features(df):
    # Превращаем текст в формат даты Pandas (авто-распознавание строки)
    datetime_col = pd.to_datetime(df['T'])
    # Вытаскиваем час (0-23), чтобы модель понимала час пик и пробки
    df['hour'] = datetime_col.dt.hour
    
    # Принудительно делаем ID текстовыми строками для CatBoost
    df['tr_id'] = df['tr_id'].astype(str)
    df['target_stop_id'] = df['target_stop_id'].astype(str)
    return df

train_data = extract_time_features(train_data)
test_data = extract_time_features(test_data)
validate_points = extract_time_features(validate_points)

# Набор признаков: теперь модель знает КТО едет, КУДА едет, текущую задержку и ЧАС суток
features = ['tr_id', 'target_stop_id', 'cur_dev_s', 'hour']
cat_features = ['tr_id', 'target_stop_id'] # Указываем текстовые колонки

X_train = train_data[features]
y_train = train_data['target_delay_s']

X_test = test_data[features]
y_test = test_data['target_delay_s']

X_validate = validate_points[features]

print("3. Обучение мощной модели CatBoost (800 шагов)...")
model = CatBoostRegressor(
    iterations=800,         # Больше деревьев для лучшей точности
    learning_rate=0.05,     # Аккуратный шаг обучения
    depth=7,                # Чуть глубже структура решений
    od_type='Iter',         # Защита от переобучения (Overfitting Detector)
    od_wait=50,             # Если точность не растет 50 шагов — стоп
    verbose=100,            # Показывать прогресс каждые 100 шагов
    random_seed=42
)

# Запускаем обучение
model.fit(
    X_train, y_train,
    eval_set=(X_test, y_test),
    cat_features=cat_features
)
model.save_model(os.path.join(BASE_DIR, "catboost_predictor.bin"))
print("Модель успешно сохранена на диск в файл catboost_predictor.bin!")

print("4. Расчет предсказаний для validate...")
preds = model.predict(X_validate)

print("5. Формирование submission.csv...")
# Загружаем оригинальный шаблон
sub = pd.read_csv(sample_sub_path, sep=';')
# Заменяем колонку ответов на новые предсказания
sub['prediction'] = preds

# Сохраняем строго с разделителем ';'
sub.to_csv(output_sub_path, sep=';', index=False)

print(f"\nУРА! Новый улучшенный файл успешно создан по адресу:\n{output_sub_path}")
print("Срочно загружайте его в раздел Data Science на платформе!")

