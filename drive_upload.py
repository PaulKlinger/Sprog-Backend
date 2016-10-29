from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def upload_sprog_to_drive():
    gauth = GoogleAuth()

    gauth.LoadCredentialsFile("google_drive_creds.txt")

    if gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()

    drive = GoogleDrive(gauth)

    sprogfile = drive.CreateFile({'id': '0B5rhAEnx4Q9wbWdkbXd1VnpzUEU'})
    sprogfile.SetContentFile("sprog.pdf")
    sprogfile.Upload()