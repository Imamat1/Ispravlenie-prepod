import sys
import os
from pathlib import Path

def switch_database(mode):
    """Переключение между режимами базы данных"""
    
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        print("❌ Файл .env не найден!")
        return
    
    # Читаем текущий .env
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Обновляем USE_POSTGRES
    updated_lines = []
    postgres_found = False
    
    for line in lines:
        if line.startswith('USE_POSTGRES='):
            if mode == 'postgres':
                updated_lines.append('USE_POSTGRES=true\n')
                print("🔄 Переключение на прямое PostgreSQL подключение...")
            else:
                updated_lines.append('USE_POSTGRES=false\n')
                print("🔄 Переключение на Supabase API...")
            postgres_found = True
        else:
            updated_lines.append(line)
    
    # Если USE_POSTGRES не найден, добавляем
    if not postgres_found:
        if mode == 'postgres':
            updated_lines.append('USE_POSTGRES=true\n')
            print("🔄 Добавление настройки PostgreSQL...")
        else:
            updated_lines.append('USE_POSTGRES=false\n')
            print("🔄 Добавление настройки Supabase API...")
    
    # Записываем обновленный .env
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    # Перезапускаем сервер
    print("🔄 Перезапуск backend сервера...")
    os.system("sudo supervisorctl restart backend")
    
    if mode == 'postgres':
        print("✅ Переключено на прямое PostgreSQL подключение!")
        print("📊 Connection: postgresql://postgres:***@db.kykzqxoxgcwqurnceslu.supabase.co:5432/postgres")
    else:
        print("✅ Переключено на Supabase API!")
        print("📊 Connection: https://kykzqxoxgcwqurnceslu.supabase.co")
    
    print("\n🚀 Для проверки:")
    print("curl https://a72883f7-06a9-42f3-b4a4-18cd6085e38a.preview.emergentagent.com/api/")

def main():
    if len(sys.argv) != 2:
        print("Использование:")
        print("  python switch_db.py supabase   # Переключиться на Supabase API")
        print("  python switch_db.py postgres   # Переключиться на прямой PostgreSQL")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode not in ['supabase', 'postgres']:
        print("❌ Неверный режим! Используйте 'supabase' или 'postgres'")
        sys.exit(1)
    
    switch_database(mode)

if __name__ == "__main__":
    main()