import re


class ChunkingService:

    ARTICLE_PATTERN = r'(?ms)^Điều\s+\d+.*?(?=^Điều\s+\d+|\Z)'
    CLAUSE_PATTERN = r'(?ms)^\d+\.\s.*?(?=^\d+\.\s|\Z)'
    POINT_PATTERN = r'(?ms)^[a-z]\)\s.*?(?=^[a-z]\)|\Z)'

    # -----------------------
    # SPLIT FUNCTIONS
    # -----------------------

    def split_articles(self, text):
        return re.findall(self.ARTICLE_PATTERN, text)

    def split_clauses(self, article):
        clauses = re.findall(self.CLAUSE_PATTERN, article)
        return clauses or [article]

    def split_points(self, clause):
        points = re.findall(self.POINT_PATTERN, clause)
        return points or [clause]

    # -----------------------
    # EXTRACT NUMBER FUNCTIONS
    # -----------------------

    def extract_article_number(self, article_text):
        """
        Match: Điều 1, Điều 15, Điều 10a (optional extension)
        """
        match = re.search(r"Điều\s+(\d+[a-zA-Z]?)", article_text)
        return match.group(1) if match else None

    def extract_clause_number(self, clause_text):
        """
        Match: 1., 2., 10.
        """
        match = re.match(r"\s*(\d+)\.", clause_text)
        return int(match.group(1)) if match else None

    def extract_point_number(self, point_text):
        """
        Match: a), b), c)
        """
        match = re.match(r"\s*([a-z])\)", point_text)
        return match.group(1) if match else None

    # -----------------------
    # OPTIONAL: CLEAN TEXT
    # -----------------------

    def clean_text(self, text):
        return re.sub(r"\s+", " ", text).strip()