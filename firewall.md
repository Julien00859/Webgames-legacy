## RPi

    # YOU SHALL NOT PASS !
    /sbin/iptables --policy INPUT DROP
    /sbin/iptables --policy OUTPUT DROP

    # loopback
    /sbin/iptables -t filter -A INPUT -i lo -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -i lo -j ACCEPT

    # icmp
    /sbin/iptables -t filter -A INPUT -p icmp -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -p icmp -j ACCEPT

    # client web
    /sbin/iptables -t filter -A INPUT -i eth0 -p tcp -sport 80 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -i eth0 -p tcp -dport 80 -m conntrack --ctstate NEW,ESTABLISED -j ACCEPT
    /sbin/iptables -t filter -A INPUT -i eth0 -p tcp -sport 443 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -i eth0 -p tcp -dport 443 -m conntrack --ctstate NEW,ESTABLISED -j ACCEPT

    # serveur ssh
    /sbin/iptables -t filter -A INPUT -i eth0 -p tcp -dport 22 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -i eth0 -p tcp -sport 22 -m conntrack --ctstate RELATED,ESTABLISED -j ACCEPT

    # client DNS
    /sbin/iptables -t filter -A INPUT -i eth0 -p udp -sport 53 -j ACCEPT
    /sbin/iptables -t filter -A INPUT -i eth0 -p tcp -sport 53 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -i eth0 -p udp -dport 53 -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -i eth0 -dport 53 -m conntrack --ctstate NEW,ESTABLISED -j ACCEPT


## debian-server 

    # YOU SHALL NOT PASS !
    /sbin/iptables --policy INPUT DROP
    /sbin/iptables --policy OUTPUT DROP

    # loopback
    /sbin/iptables -t filter -A INPUT -i lo -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -i lo -j ACCEPT

    # icmp
    /sbin/iptables -t filter -A INPUT -p icmp -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -p icmp -j ACCEPT

    # client et serveur web
    /sbin/iptables -t filter -A INPUT -i eth0 -p tcp -sport 80 -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -i eth0 -p tcp -dport 80 -j ACCEPT
    /sbin/iptables -t filter -A INPUT -i eth0 -p tcp -sport 443 -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -i eth0 -p tcp -dport 443 -j ACCEPT

    # client et serveur ssh
    /sbin/iptables -t filter -A INPUT -i eth0 -p tcp -dport 22 -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -i eth0 -p tcp -sport 22 -j ACCEPT

    # client DNS
    /sbin/iptables -t filter -A INPUT -i eth0 -p udp -sport 53 -j ACCEPT
    /sbin/iptables -t filter -A INPUT -i eth0 -p tcp -sport 53 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -i eth0 -p udp -dport 53 -j ACCEPT
    /sbin/iptables -t filter -A OUTPUT -i eth0 -dport 53 -m conntrack --ctstate NEW,ESTABLISED -j ACCEPT
