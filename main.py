import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
import time
from atproto import Client, models

# Carregar variáveis de ambiente do arquivo.env
load_dotenv()

# Configurações
twitter_username = os.getenv('TWITTER_USERNAME')
bluesky_handle = os.getenv('BLUESKY_HANDLE')
bluesky_password = os.getenv('BLUESKY_PASSWORD')
nitter_instance = os.getenv('NITTER_INSTANCE')
posted_file = 'posted_tweets.json'

# Inicializa o cliente do Bluesky
client = Client()

# Carregamento de tweets postados
def load_posted_tweets():
    try:
        with open(posted_file, 'r') as f:
            print("Carregando tweets postados.")
            return json.load(f)
    except FileNotFoundError:
        print("Nenhum tweet postado encontrado. Criando nova lista.")
        return []

# Salva o tweet postado
def save_posted_tweet(tweet):
    posted_tweets = load_posted_tweets()
    posted_tweets.append(tweet.strip())
    with open(posted_file, 'w') as f:
        json.dump(posted_tweets, f)
    print(f"Tweet postado salvo: {tweet.strip()}")

# Obtém o último tweet
def get_latest_tweet(nitter_instance, username):
    url = f"{nitter_instance}/{username}"
    print(f"Obtendo o último tweet de {username}...")
    response = requests.get(url)
    print(f"Resposta da requisição: {response.status_code}")

    if response.status_code != 200:
        print("Erro ao acessar a página do Twitter.")
        return None, None, None

    soup = BeautifulSoup(response.content, 'html.parser')
    tweets = soup.find_all('div', class_='timeline-item')
    print(f"Total de tweets encontrados: {len(tweets)}")

    for tweet in tweets:
        if tweet.find('div', class_='pinned'):
            print("Tweet fixado encontrado, ignorando...")
            continue

        video = tweet.find('div', class_='gallery-video')
        if video:
            print("Tweet com vídeo encontrado, ignorando...")
            continue  # Ignora tweets com vídeo

        image = tweet.find('div', class_='attachment image')
        caption = tweet.find('div', class_='tweet-content media-body')

        video_url = None
        if video:
            video_tag = video.find('video')
            if video_tag:
                source_tag = video_tag.find('source')
                if source_tag and 'src' in source_tag.attrs:
                    video_url = source_tag['src']

        # Verifique se a imagem existe e adicione o esquema
        image_url = image.find('a')['href'] if image else None
        if image_url and not image_url.startswith('http'):
            image_url = f"{nitter_instance}{image_url}"  # Concatena a URL base

        tweet_caption = caption.text.strip() if caption else ""

        if tweet_caption:
            print(f"Último tweet obtido: {tweet_caption}")
            return video_url, image_url, tweet_caption

    print("Nenhum tweet novo encontrado.")
    return None, None, None

# Baixa a imagem
def download_image(image_url):
    print(f"Baixando imagem de: {image_url}")
    response = requests.get(image_url)
    if response.status_code == 200:
        with open('downloaded_image.jpg', 'wb') as f:
            f.write(response.content)
        print("Imagem baixada com sucesso.")
    else:
        print(f"Falha ao baixar imagem: {response.status_code}")

# Posta no Bluesky
def post_to_bluesky(caption, image_path=None):
    print(f"Postando no Bluesky: {caption}")
    
    try:
        if image_path:
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                upload = client.upload_blob(img_data)
                images = [models.AppBskyEmbedImages.Image(alt='Descrição da imagem', image=upload.blob)]
                embed = models.AppBskyEmbedImages.Main(images=images)

                post = models.AppBskyFeedPost.Record(
                    text=caption,
                    embed=embed,
                    created_at=client.get_current_time_iso()
                )
                client.com.atproto.repo.create_record(
                    models.ComAtprotoRepoCreateRecord.Data(
                        repo=client.me.did,
                        collection=models.ids.AppBskyFeedPost,
                        record=post
                    )
                )
                print("Imagem postada com sucesso.")
        else:
            client.send_post(caption)
            print("Texto postado com sucesso.")

        print(f"Postagem realizada com sucesso.")
    except Exception as e:
        print(f"Erro ao postar no Bluesky: {e}")

# Inicializa o bot
if __name__ == "__main__":
    client.login(bluesky_handle, bluesky_password)
    print("Login no Bluesky realizado com sucesso.")
    
    while True:
        video_url, image_url, tweet_caption = get_latest_tweet(nitter_instance, twitter_username)

        if tweet_caption is None:
            print("Nenhum tweet novo encontrado.")
            time.sleep(600)  # 10 minutos
            continue

        posted_tweets = load_posted_tweets()
        print(f"Tweets postados: {posted_tweets}")

        # Remover espaços adicionais e verificar se o tweet já foi postado
        if tweet_caption.strip() not in [tweet.strip() for tweet in posted_tweets]:
            print(f"Novo tweet encontrado: {tweet_caption}")
            if image_url:
                print(f"Tentando baixar imagem de: {image_url}")
                download_image(image_url)
                print(f"Tentando postar imagem no Bluesky com o caption: {tweet_caption}")
                post_to_bluesky(tweet_caption, 'downloaded_image.jpg')
            save_posted_tweet(tweet_caption.strip())
        else:
            print(f"Tweet '{tweet_caption}' já postado anteriormente, ignorando...")

        time.sleep(600)  # 10 minutos
