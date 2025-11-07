"""
临时脚本：执行数据库迁移 - 添加步骤描述字段
"""
import pymysql

def migrate():
    # 连接数据库
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='123456',
        database='test_galaxy',
        charset='utf8mb4'
    )
    
    try:
        cursor = conn.cursor()
        
        # 执行 SQL
        sql = """
            ALTER TABLE `test_ui_case_step_execution_records` 
            ADD COLUMN `description` TEXT NULL COMMENT '步骤描述';
        """
        
        cursor.execute(sql)
        conn.commit()
        print("✅ 数据库迁移成功：已添加 description 字段")
        
    except pymysql.Error as e:
        if "Duplicate column name" in str(e):
            print("⚠️  字段已存在，跳过迁移")
        else:
            print(f"❌ 迁移失败: {e}")
            raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
