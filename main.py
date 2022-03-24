from alexa_downloader import login, get_history


def main():
    history_url = "https://www.amazon.co.uk/alexa-privacy/apd/rvh/customer-history-records"
    audio_url = "https://www.amazon.co.uk/alexa-privacy/apd/rvh/audio"

    login()

    history = get_history(history_url)

    print()


if __name__ == '__main__':
    main()
