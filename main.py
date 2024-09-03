import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip
import json
import time
from atproto import Client, models

# desenvolvido por: otavin1.bsky.social para a comunidade brasileira cronicamente online

# Carregar variáveis de ambiente do arquivo.env
load_dotenv()

# Configurações
twitter_username = os.getenv('TWITTER_USERNAME')
bluesky_handle = os.getenv('BLUESKY_USERNAME')
bluesky_password = os.getenv('BLUESKY_PASSWORD')
nitter_instance = os.getenv('NITTER_INSTANCE')
posted_file = 'posted_tweets.json'

# Configurações
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Referer': 'https://nitter.lucabased.xyz/',
    'Cookie': 'res=FD41AA63A8AC2B8F8011FB17B9DB22E7723DD34E12971'
}

# Inicializa o cliente do Bluesky
client = Client()

# carregamento de tweets postados
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
    posted_tweets.append(tweet)
    with open(posted_file, 'w') as f:
        json.dump(posted_tweets, f)
    print(f"Tweet postado salvo: {tweet}")

# Obtém o último tweet
def get_latest_tweet(nitter_instance, username):
    url = f"{nitter_instance}/{username}"
    print(f"Obtendo o último tweet de {username}...")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    video = soup.find('div', class_='gallery-video') # tag de video no html do nitter do pépito
    image = soup.find('div', class_='attachment image') # tag de imagem no html do nitter do pépito
    caption = soup.find('div', class_='tweet-content media-body') # tag de caption no html do nitter do pépito
    
    video_url = None # inicializa a variável de video_url
    if video:
        video_tag = video.find('video')
        if video_tag and 'data-url' in video_tag.attrs: # verifica se a tag video tem o atributo data-url
            video_url = video_tag['data-url']

    if video_url:
        video_url = video_url.split('/')[2] # pega o link do video

    image_url = image.find('a')['href'] if image else None # pega o link da imagem
    tweet_caption = caption.text.strip() if caption else ""

    print(f"Último tweet obtido: {tweet_caption}")
    return video_url, image_url, tweet_caption
# Baixa a imagem
def download_image(image_url):
    print(f"Baixando imagem de: {nitter_instance}{image_url}")
    response = requests.get(f"{nitter_instance}{image_url}")
    with open('downloaded_image.jpg', 'wb') as f:
        f.write(response.content)
    print("Imagem baixada com sucesso.")

# Baixa o vídeo
def download_video(video_url):
    video_path = 'downloaded_video.mp4'
    video_full_url = f"{nitter_instance}{video_url}"
    print(f"Downloading video from: {video_full_url}")
    response = requests.get(video_full_url, stream=True)

    if response.status_code == 200:
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Video downloaded successfully: {video_path}")
        return video_path
    else:
        print(f"Failed to download video: {response.status_code}")
        return None
# Converte o vídeo para GIF (AINDA NÃO TA FUNCIONAL)
# Caso alguém queira contribuir com essa parte, fique a vontade, não tive tempo para implementar
def convert_video_to_gif(video_path):
    try:
        print(f"Convertendo {video_path} para GIF...")
        clip = VideoFileClip(video_path)
        clip.write_gif('output.gif')
        print("Video converted to GIF successfully.")
    except Exception as e:
        print(f"Error converting video to GIF: {e}")

# Posta no Bluesky
def post_to_bluesky(caption, image_path=None):
    print(f"Postando no Bluesky: {caption}")
    
    if image_path:
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            upload = client.upload_blob(img_data)
            images = [models.AppBskyEmbedImages.Image(alt='Descrição da imagem', image=upload.blob)] # Adiciona a imagem ao post
            embed = models.AppBskyEmbedImages.Main(images=images)

            post = models.AppBskyFeedPost.Record(
                text=caption, # texto da postagem
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
    else:
        post = client.send_post(caption)

    print(f"Postagem realizada com sucesso.")

# Inicializa o bot
if __name__ == "__main__":
    client.login(bluesky_handle, bluesky_password)  # Autentica uma vez no início
    print("Login no Bluesky realizado com sucesso.")
    
    while True: # Loop infinito para verificar o último tweet a cada x tempo (medido em segundos)
        video_url, image_url, tweet_caption = get_latest_tweet(nitter_instance, twitter_username)

        posted_tweets = load_posted_tweets()
        if tweet_caption not in posted_tweets:
            if video_url:
                video_path = download_video(video_url)
                if video_path:
                    if os.path.getsize(video_path) > 0:
                        convert_video_to_gif(video_path)
                        post_to_bluesky(tweet_caption, 'output.gif')
                    else:
                        print("Downloaded video is empty.")
            elif image_url:
                download_image(image_url)
                post_to_bluesky(tweet_caption, 'downloaded_image.jpg')
            save_posted_tweet(tweet_caption)
        
        # Espera 10 minutos antes de verificar novamente
        print("Esperando 10 minutos antes de verificar novamente...")
        time.sleep(600) # 10 minutos