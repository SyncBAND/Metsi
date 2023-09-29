# Ionic setup - Hybrid App, webapp

### Git clone
1. [Ionic app](https://github.com/SyncBAND/Metsi.git)
2. cd Metsi/ionic

### Tested with npm 6.14.8 - node 14.15.1
https://nodejs.org/download/release/v14.15.1/

install node 14.15.1

### cd in ionic folder using terminal and run
npm i

### run build and android
npx cap add android
npx cap open android

### create web app files
ionic cap sync

- Note: everytime you make changes to the app, after you run `ionic cap sync`, the contents in the www folder in Ionic (project folder) would have changed. Use Filezilla to copy and paste the updated files on the webhost.

### possible errors in androind studio
1. Lint error - missing resources when generating android apk
- Solution: add splash.png into drawable folder i.e. res/drawable
2. Gradle build error
- Solution: replace classpath 'com.android.tools.build:gradle:4.2.1' with classpath 'com.android.tools.build:gradle:4.1.1' in build.gradle file

### Generate apk
- 'android_key' file is found in root of cloned repo


### after running 'ionic cap sync', copy files in www folder (root) and paste on the website for web app


=======================================

# Django setup - Backend setup

Read more [here](https://github.com/SyncBAND/Metsi/blob/main/django/setup.txt)

=========================================
