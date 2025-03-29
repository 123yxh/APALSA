import arxiv

# 根据单个关键词获取arxiv的文章
def get_arxiv(key_word, articles_per_keyword=10):

    search = arxiv.Search(
        query = key_word,
        max_results = articles_per_keyword,
        sort_by = arxiv.SortCriterion.SubmittedDate # 按照时间排序
    )

    return list(search.results())

# 根据多个关键词获取arxiv的文章
def get_multiple_arxiv_results(keywords, articles_per_keyword=10):
    all_results = []

    for keyword in keywords:
        try:
            print(f"正在获取关键词 '{keyword}' 的文章...")
            results = get_arxiv(keyword, articles_per_keyword)
            all_results.extend(results)
            print(f"已找到 {len(results)} 篇关于 '{keyword}' 的文章")
        except Exception as e:
            print(f"获取关键词 '{keyword}' 时出错: {e}")

    print(f"\n总计获取 {len(all_results)} 篇文章")
    return all_results


# 使用示例
# if __name__ == "__main__":
#     keywords = ["large language model", "hierarchical federated learning", "model distillation"]
#     articles = get_multiple_arxiv_results(keywords)
#
#     # 打印前3篇文章信息示例
#     for i, article in enumerate(articles[:3]):
#         print(f"\n文章 {i + 1}:")
#         print(f"标题: {article.title}")
#         print(f"作者: {', '.join(a.name for a in article.authors)}")
#         print(f"摘要: {article.summary[:200]}...")  # 只显示前200字符
#         print(f"链接: {article.pdf_url}")