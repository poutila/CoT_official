from project_paths.model import ProjectPaths
from project_paths.get_paths import write_dataclass_file
def main():
    print("Hello from pt-test!")
    # print(ProjectPaths().avatars)
    write_dataclass_file()


if __name__ == "__main__":
    main()
