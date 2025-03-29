import re
from typing import List  # 添加这行
from openai import OpenAI
import sys
sys.path.append("/home/xiaohong/yxh_l/Python_Project/Paper_Program/arxiv")
from get_arxiv import get_arxiv, get_multiple_arxiv_results

# 设置llm的服务商以及api-key
client = OpenAI(
    api_key="",
    base_url="https://api.siliconflow.cn/v1"
)

# 关键词获取专家
system_1 = '你是一个优秀的学术领域专家，能够根据用户的输入总结出细分领域的科研关键词; \
          比如给定一段用户描述‘我需要查找与大模型，联邦学习相关的分层联邦学习文章。具体而言: 涉及到模型蒸馏’，你需要严格按照以下格式返回中文以及英文缩写关键词:\
          中文关键词: 大模型, 分层联邦学习, 模型蒸馏; \
          英文关键词: llm, hfl, md'

# 相似度计算专家
system_2 = '你是一个优秀的科研领域专家，涉猎广泛，能够根据用户的描述与候选文章摘要判断两者的相似度。你应该从两个反面判断：\
            1. 关键词重合度: 根据提供的关键词在摘要中的出现次数，出现的越多评分越高; 该类的评分为1-10分;\
            2. 语义相似度: 根据提供的用户描述与候选文章摘要描述内容是否一致计算评分，描述内容越相似评分越高; 该类的评分为1-10分。\
            你需要返回总的累加分数y，你需要严格遵循以下格式返回, 不用返回你的思考以及其他回答：\
            该文章摘要的评分为: y'

# 通过大模型从用户查询中提取关键词
def get_keywords_from_query(user_query: str) -> list:
    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-14B-Instruct",
        messages=[
            {'role': 'system', 'content': system_1},
            {'role': 'user', 'content': user_query}
        ]
    )
    return extract_english_keywords(completion.choices[0].message.content)

# 在大模型的反馈中提取相似度分数
def extract_score(text: str) -> int:
    parts = text.split(":")
    if len(parts) == 2:
        return int(parts[1].strip())
    else:
        raise ValueError("文本格式不符合预期")

# 从response中提取英文关键词便于搜索
def extract_english_keywords(text: str) -> list:
    # 使用正则表达式匹配"英文关键词:"后的内容
    match = re.search(r'英文关键词:\s*([^\n;]+)', text)
    if not match:
        return []

    # 提取关键词部分，去除空格和分号，按逗号分割
    keywords_str = match.group(1).strip().rstrip(';')
    return [kw.strip() for kw in keywords_str.split(',')]

# 基于文章ID去重
def remove_duplicates(articles: List) -> List:
    seen = set()
    unique_articles = []
    for article in articles:
        if article.entry_id not in seen:
            seen.add(article.entry_id)
            unique_articles.append(article)
    return unique_articles

# 对于爬取的内容调用大模型评分
def sort_score(results, query) -> list:
    """返回包含(score, article)的列表"""
    scored_articles = []
    for article in results:
        completion = client.chat.completions.create(
            model="Qwen/Qwen2.5-14B-Instruct",
            messages=[
                {'role': 'system', 'content': system_2},
                {'role': 'user', 'content': f"用户需求: {query}\n文章摘要: {article.summary}"}
            ]
        )
        try:
            score = extract_score(completion.choices[0].message.content)
            scored_articles.append((score, article))
        except Exception as e:
            print(f"评分出错: {e}")
            scored_articles.append((0, article))  # 默认分数
    return scored_articles

def main():

    # 获取用户的输入
    user_query = input("请输入您的研究需求描述: ")

    # 通过大模型提取关键词
    keywords = get_keywords_from_query(user_query)
    print(f"\n识别到的关键词: {', '.join(keywords)}")

    # 获取相关文章
    paper_number = 10
    articles = get_multiple_arxiv_results(keywords, paper_number)
    articles = remove_duplicates(articles)
    print(f"\n共检索到 {len(articles)} 篇相关文章")

    # 评分和排序
    scored_articles = sort_score(articles, user_query)
    scored_articles.sort(reverse=True, key=lambda x: x[0])  # 按分数降序

    # 输出top-k结果
    top_k = 10
    print(f"\n===== 推荐的前{top_k}篇文章 =====")
    for i, (score, article) in enumerate(scored_articles[:top_k]):
        print(f"\n[第{i + 1}名]评分: {score}")
        print(f"标题: {article.title}")
        print(f"作者: {', '.join(a.name for a in article.authors[:3])}等")
        print(f"摘要: {article.summary[:200]}...")
        print(f"链接: {article.pdf_url}")
        print(f"发表日期: {article.published.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    main()  # 确保这行存在
