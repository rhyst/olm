class ArticleStatus:
    ACTIVE = 1
    UNLISTED = 2
    DRAFT = 3

class Signals:
    INITIALISED             = "INITIALISED"             # args: context
    AFTER_ARTICLE_READ      = "AFTER_ARTICLE_READ"      # args: context, article
    AFTER_ALL_ARTICLES_READ = "AFTER_ALL_ARTICLES_READ" # args: context, articles
    BEFORE_WRITING          = "BEFORE_WRITING"          # args: context