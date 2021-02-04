# vbb_notification
This is a small application for daily trip departure notification. The notification is done using the VBB information and taking into account the place of origin and the place you want to reach. As well as the desired time of the journey and how long before you want to receive the notification.

## Install
Do you need have pip install in the system.
Run the following command:
```shel
pip install git+https://github.com/npujol/vbb_notification.git
```

## Usage
Run the following command:
```shel
poetry run vbb setup-vbbjourney
```

## Default
The default values are the followings
- Keywords about your current location [pankow]
- Keywords about the location you want to reach [alexanderplatz]
- Time to make the daily commute (hh:mm) [18:00]
- Advance notice time (number) [15]
