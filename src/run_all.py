from .ingest import ingest
from .analysis import main as analyze
from .export_dashboard import main as export
from .render_findings import main as render

def main():
    ingest()
    analyze()
    export()
    render()

if __name__=='__main__':main()
