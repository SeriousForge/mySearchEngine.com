import re

# Regular expression to find href links in HTML
HREF_RE = re.compile(r'<(?:a|area)\s[^>]*?href\s*=\s*(?:[\'"]([^\'"]+)[\'"]|([^\s>]+))', re.IGNORECASE | re.DOTALL)
SCRIPT_STYLE_RE = re.compile(r"(?is)<(script|style)\b.*?>.*?</\1>")
TAG_RE = re.compile(r"(?s)<[^>]+>")
TITLE_RE = re.compile(r"(?is)<title>(.*?)</title>")

def check_stopword(word):
    stopwords = [
        "a", 'able', 'about', 'above', 'according', 'accordingly', 'across', 'actually', 'after','afterwards', 'again', 'against', "ain",
        'all', 'allow', 'allows', 'almost', 'alone', 'along','already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'an', 'and',
        'another','any', 'anybody', 'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'apart','appear', 'appreciate', 'appropriate',
        'are', "aren", 'around', 'as', 'aside', 'ask', 'asking','associated', 'at', 'available', 'away', 'awfully', 'be', 'became', 'because',
        'become', 'becomes','becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'believe', 'below', 'beside', 'besides','best', 'better',
        'between', 'beyond', 'both', 'brief', 'but', 'by', "c", "mon", 'came', "can",'cannot', 'cant', 'cause', 'causes', 'certain', 'certainly', 'changes',
        'clearly', 'co', 'com', 'come','comes', 'concerning', 'consequently', 'consider', 'considering', 'contain', 'containing', 'contains','corresponding',
        'could', "couldn", 'course', 'currently', 'definitely', 'described', 'despite', 'did',"didn", 'different', 'do', 'does', "doesn", 'doing', "don",
        'done', 'down', 'downwards', 'during', 'each','edu', 'eg', 'eight', 'either', 'else', 'elsewhere', 'enough', 'entirely', 'especially', 'et', 'etc',
        'even', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'exactly','example', 'except', 'far', 'few', 'fifth', 'first',
        'five', 'followed', 'following', 'follows','for', 'former', 'formerly', 'forth', 'four', 'from', 'further', 'furthermore', 'get', 'gets','getting',
        'given', 'gives', 'go', 'goes', 'going', 'gone', 'got', 'gotten', 'greetings', 'had', "hadn",'happens', 'hardly', 'has', "hasn", 'have', "haven",
        'having', 'he', 'hello', 'help', 'hence', 'her','here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'hi', 'him', 'himself', 'his',
        'hither', 'hopefully', 'how', 'howbeit', 'however', "i", 'ie', 'if', 'ignored', 'immediate', 'in','inasmuch', 'inc', 'indeed', 'indicate', 'indicated',
        'indicates', 'inner', 'insofar', 'instead', 'into','inward', 'is', "isn", 'it', 'its', 'itself', 'just', 'keep', 'keeps', 'kept', 'know', 'known',
        'knows','last', 'lately', 'later', 'latter', 'latterly', 'least', 'less', 'lest', 'let', 'like', 'liked', 'likely','little', 'look', 'looking', 'looks',
        'ltd', 'mainly', 'many', 'may', 'maybe', 'me', 'mean', 'meanwhile','merely', 'might', 'more', 'moreover', 'most', 'mostly', 'much', 'must', 'my', 'myself',
        'name', 'namely','nd', 'near', 'nearly', 'necessary', 'need', 'needs', 'neither', 'never', 'nevertheless', 'new', 'next','nine', 'no', 'nobody', 'non',
        'none', 'noone', 'nor', 'normally', 'not', 'nothing', 'novel', 'now', 'nowhere','obviously', 'of', 'off', 'often', 'oh', 'ok', 'okay', 'old', 'on', 'once',
        'one', 'ones', 'only', 'onto', 'or','other', 'others', 'otherwise', 'ought', 'our', 'ours', 'ourselves', 'out', 'outside', 'over', 'overall', 'own','particular',
        'particularly', 'per', 'perhaps', 'placed', 'please', 'plus', 'possible', 'presumably', 'probably','provides', 'que', 'quite', 'qv', 'rather', 'rd', 're',
        'really', 'reasonably', 'regarding', 'regardless', 'regards','relatively', 'respectively', 'right', 'said', 'same', 'saw', 'say', 'saying', 'says', 'second',
        'secondly', 'see', 'seeing','seem', 'seemed', 'seeming', 'seems', 'seen', 'self', 'selves', 'sensible', 'sent', 'serious', 'seriously', 'seven', 'several',
        'shall', 'she', 'should', "shouldn", 'since', 'six', 'so', 'some', 'somebody', 'somehow', 'someone', 'something', 'sometime','sometimes', 'somewhat',
        'somewhere', 'soon', 'sorry', 'specified', 'specify', 'specifying', 'still', 'sub', 'such', 'sup','sure', "s", "t", 'take', 'taken', 'tell', 'tends', 'th',
        'than', 'thank', 'thanks', 'thanx', 'that', 'thats', 'the', 'their','theirs', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby',
        'therefore', 'therein', 'theres', 'thereupon','these', 'they', "ll", "ve", 'think', 'third', 'this', 'thorough', 'thoroughly', 'those', 'though', 'three',
        'through', 'throughout','thru', 'thus', 'to', 'together', 'too', 'took', 'toward', 'towards', 'tried', 'tries', 'truly', 'try', 'trying', 'twice', 'two',
        'un', 'under', 'unfortunately', 'unless', 'unlikely', 'until', 'unto', 'up', 'upon', 'us', 'use', 'used', 'useful', 'uses','using', 'usually', 'value',
        'various', 'very', 'via', 'viz', 'vs', 'want', 'wants', 'was', 'way', 'we', "d", 'welcome', 'well','went', 'were', "weren", 'what', 'whatever', 'when',
        'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein','whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who',
        'whoever', 'whole', 'whom', 'whose', 'why', 'will','willing', 'wish', 'with', 'within', 'without', "won", 'wonder', 'would', "wouldn", 'yes', 'yet',
        'you', 'your', 'yours','yourself', 'yourselves', 'zero']
    
    if word in stopwords:
        return True
    return False

def extract_words_from_html(text):
    text = SCRIPT_STYLE_RE.sub(" ", text)
    text = TAG_RE.sub(" ", text)

    words = []
    current_word = []

    for char in text:
        if char.isalpha():
            current_word.append(char)
        else:
            if current_word:
                words.append(''.join(current_word))
                current_word = []
    
    if current_word:
        words.append(''.join(current_word))

    return [w.lower() for w in words if not check_stopword(w.lower())]

def extract_links_from_html(text):
    links = []
    # updated to get quoted and unquoted links, ex. href="link", href=link
    for match in HREF_RE.findall(text):
        link = (match[0] or match[1]).strip()
        if link:
            links.append(link)
    return links

# Tokenizes a query string into lowercase words, ignoring non-alphabetic characters
QUERY_RE = re.compile(r"[A-Za-z]+")
def tokenize_query(text: str):
    tokens = [w.lower() for w in QUERY_RE.findall(text)]
    return tokens