STOP() {
	echo Delete old rules
	/sbin/iptables -X
	/sbin/iptables -F

	echo Set policy to ACCEPT
	/sbin/iptables --policy INPUT ACCEPT
	/sbin/iptables --policy FORWARD ACCEPT
	/sbin/iptables --policy OUTPUT ACCEPT
}

START() {
	echo "Delete old rules"
	/sbin/iptables -X
	/sbin/iptables -F
	
	echo "Allow Loop-Back"
	/sbin/iptables -t filter -A INPUT -i lo -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -o lo -j ACCEPT

	echo "Allow ICMP"
	/sbin/iptables -t filter -A INPUT -p icmp -j ACCEPT
	/sbin/iptables -t filter -A FORWARD -p icmp -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p icmp -j ACCEPT
	
	echo "Deny new connection from 192.168.1.0/24 to 192.168.0.0/24"
	/sbin/iptables -t filter -A FORWARD -s 192.168.1.0/24 -d 192.168.0.0/24 -m conntrack --ctstate NEW -j DROP

	echo "NAT for 192.168.1.0/24"
	/sbin/iptables -t nat -A POSTROUTING -o ens192 -s 192.168.1.0/0 -d 0.0.0.0/0 -j MASQUERADE

	echo "Allow HTTP client and server"
	/sbin/iptables -t filter -A INPUT -p tcp --sport 80 -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p tcp --dport 80 -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p tcp --sport 80 -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p tcp --dport 80 -j ACCEPT

	echo "Allow HTTPS client and server"
	/sbin/iptables -t filter -A INPUT -p tcp --sport 443 -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p tcp --dport 443 -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p tcp --sport 443 -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p tcp --dport 443 -j ACCEPT
	
	echo "Allow SSH client and server"
	/sbin/iptables -t filter -A INPUT -p tcp --sport 22 -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p tcp --dport 22 -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p tcp --sport 22 -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p tcp --dport 22 -j ACCEPT

	echo "Allow DNS as client"
	/sbin/iptables -t filter -A INPUT -p udp --sport 53 -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p tcp --sport 53 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p udp --dport 53 -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p tcp --dport 53 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT

	echo "Allow NFS as server for 192.168.1.0/24"
	/sbin/iptables -t filter -A INPUT -p tcp --dport 2049 -s 192.168.1.0/24 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p udp --dport 2049 -s 192.168.1.0/24 -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p tcp --sport 2049 -d 192.168.1.0/24 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p udp --sport 2049 -d 192.168.1.0/24 -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p tcp --dport 111 -s 192.168.1.0/24 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p udp --dport 111 -s 192.168.1.0/24 -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p tcp --sport 111 -d 192.168.1.0/24 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p udp --sport 111 -d 192.168.1.0/24 -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p tcp --dport 4000 -s 192.168.1.0/24 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p udp --dport 4000 -s 192.168.1.0/24 -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p tcp --sport 4000 -d 192.168.1.0/24 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p udp --sport 4000 -d 192.168.1.0/24 -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p tcp --dport 4001 -s 192.168.1.0/24 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p udp --dport 4001 -s 192.168.1.0/24 -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p tcp --sport 4001 -d 192.168.1.0/24 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p udp --sport 4001 -d 192.168.1.0/24 -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p tcp --dport 4002 -s 192.168.1.0/24 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p udp --dport 4002 -s 192.168.1.0/24 -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p tcp --sport 4002 -d 192.168.1.0/24 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p udp --sport 4002 -d 192.168.1.0/24 -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p tcp --dport 4003 -s 192.168.1.0/24 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
	/sbin/iptables -t filter -A INPUT -p udp --dport 4003 -s 192.168.1.0/24 -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p tcp --sport 4003 -d 192.168.1.0/24 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
	/sbin/iptables -t filter -A OUTPUT -p udp --sport 4003 -d 192.168.1.0/24 -j ACCEPT

	echo "Set default policy"
	/sbin/iptables --policy INPUT DROP
	/sbin/iptables --policy FORWARD ACCEPT
	/sbin/iptables --policy OUTPUT DROP
}

case $1 in
	start)
		START
		;;
	stop)
		STOP
		;;
	*)
		echo "Usage: $0 {start|stop}"
esac

