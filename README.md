# What is Gallery?

Gallery is a placeholder name for what is intended to be a federated art 
gallery.  If you prefer a fancy self-referential acronym...:

**G**allery's  
**A**nother  
**L**ittle  
**L**ightweight  
**E**lectronic  
**R**ecursive  
**Y**ggdrasil

# Federation?

Federation means that it works with other instances running Gallery.  Think of email:  a gmail user can email a hotmail user and it *just works*.  [Mastodon](https://mastodon.social) is another famous example of federated software.  You can also host your own instance and follow profiles on other instances.

# Setup

Setup currently assumes an Ubuntu 16.06 box.  After a fresh install:

- `wget https://raw.githubusercontent.com/almafeta/gallery/master/setup.sh`
- `chmod 764 setup.sh`
- `sudo /home/username/setup.sh`

Enter your password and let it run.

Once set up, it won't do terribly much yet, since it's still pre-Core.
