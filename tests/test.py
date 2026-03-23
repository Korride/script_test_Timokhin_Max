import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from main import CoffeeMedianReport, ReportContext, read_csv_files

class TestCriticalFunctionality:

    @pytest.fixture
    def report(self):
        return CoffeeMedianReport()

    @pytest.fixture
    def csv_data(self):
        csv_path = Path(__file__).parent.parent / 'CSV src/math.csv'
        if csv_path.exists():
            return read_csv_files([str(csv_path)])
        return []

    def test_1_core_median_calculation(self, report, csv_data):

        #Тест 1: Расчет медиан и сортировка

        results = report.process(csv_data)
        formatted = report.format_output(results)
        headers = report.get_headers()

        assert report.get_name() == "median_coffee"
        assert len(results) == 15
        assert len(formatted) == 15
        assert headers == ["Student", "median_coffee"]

        medians = [r[1] for r in results]
        assert medians == sorted(medians, reverse=True)

        alexey = next(r for r in results if r[0] == 'Алексей Смирнов')
        assert alexey[1] == 500.0

        ivan_formatted = next(r for r in formatted if r[0] == 'Иван Кузнецов')
        assert ivan_formatted[1] == '650.00'

    def test_2_error_handling(self, report, capsys):

        #Тест 2: Обработка ошибок

        data = [
            {'student': 'Иванов', 'coffee_spent': '200'},
            {'student': 'Иванов', 'coffee_spent': 200},
            {'student': 'Иванов', 'coffee_spent': 'invalid'},
            {'student': 'Иванов', 'coffee_spent': 'abc123'},
            {'student': '', 'coffee_spent': '300'},
            {'student': '   ', 'coffee_spent': '400'},
            {'student': 'Петров'},
            {'coffee_spent': '500'},
            {'student': 'Сидоров', 'coffee_spent': '100'},
            {'student': 'Сидоров', 'coffee_spent': '200'},
            {'student': 'Кузнецов', 'coffee_spent': None},
        ]

        results = report.process(data)

        assert len(results) == 3
        assert results[0][0] == 'Иванов'
        assert results[0][1] == 200.0

        captured = capsys.readouterr()
        assert "Warning: incorrect value coffee_spent" in captured.err
        warning_count = captured.err.count("Warning: incorrect value coffee_spent")
        assert warning_count >= 2

    def test_3_edge_cases(self, report):

        #Тест 3: Граничные случаи

        assert report.process([]) == []

        data1 = [{'student': 'Иванов', 'coffee_spent': '100'}]
        results1 = report.process(data1)
        assert results1[0][1] == 100.0

        data2 = [
            {'student': 'Иванов', 'coffee_spent': '100'},
            {'student': 'Иванов', 'coffee_spent': '200'},
        ]
        results2 = report.process(data2)
        assert results2[0][1] == 150.0

        data3 = [
            {'student': 'Иванов', 'coffee_spent': '100'},
            {'student': 'Иванов', 'coffee_spent': '200'},
            {'student': 'Иванов', 'coffee_spent': '300'},
        ]
        results3 = report.process(data3)
        assert results3[0][1] == 200.0

        data4 = [
            {'student': 'Иванов', 'coffee_spent': '0'},
            {'student': 'Иванов', 'coffee_spent': '0'},
            {'student': 'Иванов', 'coffee_spent': '100'},
        ]
        results4 = report.process(data4)
        assert results4[0][1] == 0.0

    def test_4_context_workflow(self):

        #Тест 4: Работа контекста

        context = ReportContext()

        context.register_strategy(CoffeeMedianReport())

        available = context.get_available_reports()
        assert "median_coffee" in available

        context.set_strategy("median_coffee")

        data = [
            {'student': 'Иванов', 'coffee_spent': '100'},
            {'student': 'Иванов', 'coffee_spent': '200'},
        ]

        table_data, headers = context.execute_report(data)

        assert headers == ["Student", "median_coffee"]
        assert len(table_data) == 1
        assert table_data[0][0] == 'Иванов'
        assert table_data[0][1] == '150.00'

    def test_5_context_errors(self):

        #Тест 5: Обработка ошибок контекста

        context = ReportContext()

        with pytest.raises(ValueError, match="Strategy invalid not registered"):
            context.set_strategy("invalid")

        with pytest.raises(ValueError, match="No strategy selected"):
            context.execute_report([])

        context.register_strategy(CoffeeMedianReport())
        context.set_strategy("median_coffee")

        data = [{'student': 'Иванов', 'coffee_spent': '100'}]
        table_data, _ = context.execute_report(data)
        assert len(table_data) == 1

    def test_6_csv_reading_and_integration(self, csv_data):

        #Тест 6: Чтение CSV и интеграция

        assert len(csv_data) == 45

        students = set(row['student'] for row in csv_data)
        expected_students = {
            'Алексей Смирнов', 'Дарья Петрова', 'Иван Кузнецов',
            'Мария Соколова', 'Павел Новиков', 'Елена Волкова',
            'Дмитрий Морозов', 'Анна Белова', 'Сергей Козлов',
            'Ольга Новикова', 'Никита Соловьев', 'Татьяна Васильева',
            'Артем Григорьев', 'Виктория Федорова', 'Михаил Павлов'
        }
        assert students == expected_students

        context = ReportContext()
        context.register_strategy(CoffeeMedianReport())
        context.set_strategy("median_coffee")

        table_data, headers = context.execute_report(csv_data)

        medians = [float(row[1]) for row in table_data]
        assert medians == sorted(medians, reverse=True)

        assert medians[0] == 650.0
        assert medians[-1] == 120.0