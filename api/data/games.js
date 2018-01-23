const games = [
  {g_name: 'Bomberman', g_status: true, g_numbers_needed_count: 4, g_path: '/usr/opt/bomberman', g_image: 'bomberman.sh', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Robotwar', g_status: false, g_numbers_needed_count: 4, g_path: '/usr/opt/robotwar', g_image: 'robotwar.sh', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Tetris', g_status: true, g_numbers_needed_count: 4, g_path: '/usr/opt/tetris', g_image: 'tetris.py', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Tower Defense', g_status: false, g_numbers_needed_count: 4, g_path: '/usr/opt/tower-defense', g_image: 'tower.py', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Chess Titan', g_status: true, g_numbers_needed_count: 4, g_path: '/usr/opt/chess', g_image: 'chess.js', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Pinball', g_status: false, g_numbers_needed_count: 4, g_path: '/usr/opt/pinball', g_image: 'pinball.jar', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Spyfall', g_status: true, g_numbers_needed_count: 4, g_path: '/usr/opt/spyfall', g_image: 'spyfall.jar', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Labyrinthe', g_status: true, g_numbers_needed_count: 4, g_path: '/usr/opt/labyrinthe', g_image: 'labyrinthe.sh', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Cluedo', g_status: true, g_numbers_needed_count: 4, g_path: '/usr/opt/cluedo', g_image: 'cluedo.js', g_ports: {"udp": [2000, 2100]}},
  {g_name: 'Go - Deluxe Edition', g_status: false, g_numbers_needed_count: 4, g_path: '/usr/opt/go', g_image: 'go.js', g_ports: {"udp": [2000, 2100]}}
];

module.exports = games;
