import argparse
import csv
import sys
import statistics
from operator import itemgetter
from collections import defaultdict
from abc import ABC, abstractmethod
from tabulate import tabulate

class ReportStrategy(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass
    @abstractmethod
    def process(self,data: list) -> list:
        pass
    @abstractmethod
    def format_output(self,results: list) -> list:
        pass
    @abstractmethod
    def get_headers(self) -> list:
        pass

class CoffeeMedianReport(ReportStrategy):
    def get_name(self) -> str:
        return "median_coffee"

    def process(self,data: list) -> list:
        student_coffee_spends = defaultdict(list)

        for row in data:
            student = row.get('student','').strip()
            try:
                coffee_spent = row.get('coffee_spent', 0)

                if coffee_spent is None:
                    continue

                if isinstance(coffee_spent, str):
                    coffee_spent = float(coffee_spent)
                if student: student_coffee_spends[student].append(coffee_spent)
            except (ValueError, TypeError):
                print(f"Warning: incorrect value coffee_spent in row: {row}", file=sys.stderr)
                continue

        results =  []
        for student,spends in student_coffee_spends.items():
            if spends:
                median = statistics.median(spends)
                results.append((student, median))
            else:
                results.append((student, 0.0))

        results.sort(key=itemgetter(1), reverse=True)

        return results

    def format_output(self,results: list) -> list:
        table_data = []
        for student, median in results:
            table_data.append([student, f"{median:.2f}"])
        return table_data

    def get_headers(self) -> list:
        return ["Student", "median_coffee"]
    #Далее можем описать классы иных стратегий

class ReportContext:
    def __init__(self):
        self.strategies = {}
        self._current_strategy = None

    def register_strategy(self, strategy: ReportStrategy):
        self.strategies[strategy.get_name()] = strategy

    def set_strategy(self, report_name:str):
        if report_name not in self.strategies:
            raise ValueError(f"Strategy {report_name} not registered")
        self._current_strategy = self.strategies[report_name]

    def get_available_reports(self) -> list:
        return list(self.strategies.keys())

    def execute_report(self, data: list) -> tuple:
        if not self._current_strategy:
            raise ValueError("No strategy selected")

        results = self._current_strategy.process(data)
        formatted_data = self._current_strategy.format_output(results)
        headers = self._current_strategy.get_headers()

        return formatted_data, headers

def read_csv_files(file_names):

   all_data=[]

   for file_name in file_names:
           with open(file_name, 'r', encoding='utf8') as file:
               reader = csv.DictReader(file)
               rows = list(reader)
               all_data.extend(rows)

   return all_data

def main():
    parser = argparse.ArgumentParser(description='Calculating selected method',
                                     formatter_class=argparse.RawTextHelpFormatter,)
    parser.add_argument('--files', nargs='+', required=True, help='Files to process')
    parser.add_argument('--report', required=True, help='Request for run')

    args = parser.parse_args()

    context = ReportContext()

    context.register_strategy(CoffeeMedianReport())
    #Тут регистрируем иные стратегии



    if args.report not in context.get_available_reports():
        available = ", ".join(context.get_available_reports())
        print(f"Warning: Unknown report '{args.report}'. Available reports: {available}", file=sys.stderr)
        sys.exit(1)

    context.set_strategy(args.report)

    data = read_csv_files(args.files)

    if not data:
        print("No data", file=sys.stderr)
        sys.exit(1)

    table_data, headers = context.execute_report(data)

    if not table_data:
        print("No results", file=sys.stderr)
        sys.exit(0)

    print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid", numalign="center"))

if __name__ == '__main__':
    main()