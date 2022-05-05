from alexa_downloader import AlexaDownloader


def main():
    alexa = AlexaDownloader()
    alexa.login()

    history = alexa.get_history()

    print()


if __name__ == '__main__':
    main()
