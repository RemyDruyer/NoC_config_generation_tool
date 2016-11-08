
--------------------------------------------------------------
-- IP   	: noc_config PACKAGE              			--
-- AUTHOR 	: R.Druyer                              			--
-- DATE   	:  8 novembre 2016                           		--
-- VERSION	: 1.6                                   				--
--------------------------------------------------------------


library IEEE;
use IEEE.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.log2;
use ieee.math_real.ceil;

package noc_config is

----------------------------------------------------------------
				----- GLOBAL CONSTANTS  -----
----------------------------------------------------------------
constant 	TOTAL_MASTER_NB   				: integer := 16;
constant 	TOTAL_SLAVE_NB   				: integer := 13;
constant 	TOTAL_ROUTER_CONNEXIONS 	: integer := 7;
constant 	TOTAL_ROUTING_PORT_NB 		: integer := TOTAL_ROUTER_CONNEXIONS*2;
constant 	TOTAL_ROUTER_NB   				: integer := 6;
	
constant 	SECURITY_MONITOR_ACTIVATION   : integer := 1; -- 0 = monitors deactivated ; 1 = monitors activated

----------------------------------------------------------------
						----- FIXED PART -----
----------------------------------------------------------------
-- INTEGER --
constant	DATA_WIDTH						: integer := 32; 	--(in bits)
constant	ADD_SIZE   							: integer := 32; 	--(in bits)
constant	PORT_ADD_SIZE 						: integer := 4; 	--(in bits)
constant	ROUTER_ADD_SIZE 					: integer := 6; 	--(in bits)
constant	NOC_ADD_SIZE   						: integer := PORT_ADD_SIZE + ROUTER_ADD_SIZE; --(in bits)
constant	BYTEENABLE_SIZE					: integer := 4;	--(in 4-bits)
constant	REQSIZE_VECTOR_SIZE				: integer := 8;	--(define the size of the std_logic_vector of REQSIZE) example : if REQSIZE_VECTOR_SIZE = 8 -> REQSIZE can count 2^REQSIZE_VECTOR_SIZE = 256 bytes
constant 	MAX_PORT_NB_BY_ROUTER			: integer := 16;
constant	PACKET_PAYLOAD_MAXIMUM_FLITSIZE	: integer := 8; 						--(in 32 bits words)
constant 	MAX_REQSIZE_in_byte					: integer := PACKET_PAYLOAD_MAXIMUM_FLITSIZE*4; 	--(in 32 bits words)
constant 	MASTER_ADDRESS_DECODER_RANGE	: integer := 32;

-- FIFO ALTERA --
constant 	ROUTING_PORT_FIFO_DATA_DEPTH	: integer := 8;
constant 	ROUTING_PORT_FIFO_ADDR_WIDTH	: integer := 3; -- = log2(FIFO_ALTERA_DATA_DEPTH)

-- constant FIFO_ALTERA_DATA_DEPTH	: integer := 16;
-- constant FIFO_ALTERA_ADDR_WIDTH	: integer := 4; -- = log2(FIFO_ALTERA_DATA_DEPTH)

-- constant FIFO_ALTERA_DATA_DEPTH	: integer := 256;
-- constant FIFO_ALTERA_ADDR_WIDTH	: integer := 8; -- = log2(FIFO_ALTERA_DATA_DEPTH)

---- FIFO DEPTH MUST BE AT LEAST EQUAL TO MAXIMUM PACKET PAYLOAD SIZE + 1 AND MUST BE POWER OF 2
constant	ACK_PACKETIZER_FIFO_DEPTH 		: integer := 16;
-- packetizer address width must be a log2 of PACKETIZER_FIFO_DEPTH
constant	ACK_PACKETIZER_FIFO_ADDR_WIDTH 	: integer := 4;

-- SUBTYPE --
subtype 	regADD			is std_logic_vector((ADD_SIZE-1) downto 0);
subtype 	regPORTADD 	is std_logic_vector((PORT_ADD_SIZE-1) downto 0);
subtype 	regROUTERADD 	is std_logic_vector((ROUTER_ADD_SIZE-1) downto 0);
subtype 	regNOCADD 		is std_logic_vector((NOC_ADD_SIZE-1) downto 0);
subtype 	regDATA 		is std_logic_vector((DATA_WIDTH-1) downto 0);
subtype 	regBYTEENAB 	is std_logic_vector((BYTEENABLE_SIZE-1) downto 0);
subtype 	regREQSIZE 		is std_logic_vector((REQSIZE_VECTOR_SIZE-1) downto 0);
subtype 	reg32 			is std_logic_vector(31 downto 0);

-- REG CONSTANT --
constant	reg_PACKET_PAYLOAD_MAX_FLITSIZE 	: regREQSIZE := std_logic_vector(to_unsigned(PACKET_PAYLOAD_MAXIMUM_FLITSIZE,8));
constant	reg_PACKET_PAYLOAD_MAX_BYTESIZE 	: regREQSIZE := std_logic_vector(to_unsigned(PACKET_PAYLOAD_MAXIMUM_FLITSIZE*4,8));

-- SIZE ARRAY --
type 	arrayADD			is array(natural RANGE <>) of regADD;
type 	arrayPORTADD 		is array(natural RANGE <>) of regPORTADD;
type 	arrayROUTERADD 	is array(natural RANGE <>) of regROUTERADD;
type 	arrayNOCADD 		is array(natural RANGE <>) of regNOCADD;
type 	arrayDATA 			is array(natural RANGE <>) of regDATA;
type 	arrayBYTEENAB 		is array(natural RANGE <>) of regBYTEENAB;
type 	arrayREQSIZE 		is array(natural RANGE <>) of regREQSIZE;
type 	array32				is array(natural RANGE <>) of reg32;


-- RECORD --
type record_master_interface_address_decode_routing_table is record
	SLAVE_BASE_ADD 					: regADD;
	SLAVE_HIGH_ADD					: regADD;
	LOCAL_PORT_DESTINATION_ADD 		: regPORTADD;
	PACKET_DESTINATION_ADD 			: regNOCADD;
end record;

type record_routing_table is record
	ROUTER_DESTINATION_ADD			: regROUTERADD;
	LOCAL_PORT_DESTINATION_ADD 		: regPORTADD;
end record;

type record_master_routport_slave_nb_by_router is record
	MASTER_NB						: integer;
	SLAVE_NB						: integer;
	ROUTING_PORT_NB					: integer;
end record;

type record_router_connexion is record
	SOURCE_ROUTER					: integer;
	SOURCE_ROUTING_PORT				: integer;
	DESTINATION_ROUTER				: integer;
	DESTINATION_ROUTING_PORT		: integer;
end record;

type record_packet_master is record
	REQ_PM							: std_logic;
	DOUT_PM							: regDATA;
	ACK_PM							: std_logic;
end record;

type record_packet_slave is record
	REQ_PS							: std_logic;
	DIN_PS							: regDATA;
	ACK_PS							: std_logic;
end record;

type record_decod_add_parameter is record
	MASTER_TABLE_RANK_NB			: integer;
	MASTER_DECOD_TABLE_SIZE			: integer;
end record;

-- ARRAY --

--Routing table
type routing_table_array is array (0 to TOTAL_ROUTER_NB-2) of record_routing_table;
type array_all_routing_tables is array (0 to TOTAL_ROUTER_NB-1) of routing_table_array;
--Master and slave numbers by router
type array_all_record_master_routport_slave_nb_by_router is array (0 to TOTAL_ROUTER_NB-1) of record_master_routport_slave_nb_by_router;
--Packet interface port address
type packet_interface_portadd_vector is array (0 to 15) of integer;
type array_all_router_packet_interface_portadd is array (0 to TOTAL_ROUTER_NB-1) of packet_interface_portadd_vector;

--Router connexions
type array_all_router_connexion is array (0 to TOTAL_ROUTER_CONNEXIONS-1) of record_router_connexion;
--Routing ports by router
type vector_all_router_routing_port_nb is array (0 to TOTAL_ROUTER_NB-1) of integer;

--RANK (indicates the rank of master and slave into the general vector)
type master_rank_in_vector is array (0 to TOTAL_ROUTER_NB-1) of integer;
type slave_rank_in_vector is array (0 to TOTAL_ROUTER_NB-1) of integer;

--Master packet interfaces
type array_ROUTING_PORT_REQ_PM is array (0 to TOTAL_ROUTER_NB-1) of std_logic_vector(0 to 15);
type array_ROUTING_PORT_DOUT_PM is array (0 to TOTAL_ROUTER_NB-1) of arrayDATA(0 to 15);
type array_ROUTING_PORT_ACK_PM is array (0 to TOTAL_ROUTER_NB-1) of std_logic_vector(0 to 15);
--Slave packet interfaces
type array_ROUTING_PORT_REQ_PS is array (0 to TOTAL_ROUTER_NB-1) of std_logic_vector(0 to 15);
type array_ROUTING_PORT_DIN_PS is array (0 to TOTAL_ROUTER_NB-1) of arrayDATA(0 to 15);
type array_ROUTING_PORT_ACK_PS is array (0 to TOTAL_ROUTER_NB-1) of std_logic_vector(0 to 15);

--IOmux local matrix
type integer_vector is array (0 to 16) of integer;
type local_connexion_matrix is array (0 to 16) of integer_vector;
type array_all_local_connexion_matrix is array (0 to TOTAL_ROUTER_NB-1) of local_connexion_matrix;

--decoding address table matrix
type vector_add_decoder_parameter is array (0 to 14) of record_decod_add_parameter;
type matrix_add_decoder_parameter is array (0 to TOTAL_ROUTER_NB-1) of vector_add_decoder_parameter;


-- ROUTER, MASTER and SLAVE ADDRESSES (in bits) --
constant ROUTER0 : regROUTERADD:= "000000";
constant ROUTER1 : regROUTERADD:= "000001";
constant ROUTER2 : regROUTERADD:= "000010";
constant ROUTER3 : regROUTERADD:= "000011";
constant ROUTER4 : regROUTERADD:= "000100";
constant ROUTER5 : regROUTERADD:= "000101";
constant ROUTER6 : regROUTERADD:= "000110";
constant ROUTER7 : regROUTERADD:= "000111";
constant ROUTER8 : regROUTERADD:= "001000";
constant ROUTER9 : regROUTERADD:= "001001";

constant ROUTER10 : regROUTERADD:= "001010";
constant ROUTER11 : regROUTERADD:= "001011";
constant ROUTER12 : regROUTERADD:= "001100";
constant ROUTER13 : regROUTERADD:= "001101";
constant ROUTER14 : regROUTERADD:= "001110";
constant ROUTER15 : regROUTERADD:= "001111";
constant ROUTER16 : regROUTERADD:= "010000";
constant ROUTER17 : regROUTERADD:= "010001";
constant ROUTER18 : regROUTERADD:= "010010";
constant ROUTER19 : regROUTERADD:= "010011";

constant ROUTER20 : regROUTERADD:= "010100";
constant ROUTER21 : regROUTERADD:= "010101";
constant ROUTER22 : regROUTERADD:= "010110";
constant ROUTER23 : regROUTERADD:= "010111";
constant ROUTER24 : regROUTERADD:= "011000";
constant ROUTER25 : regROUTERADD:= "011001";
constant ROUTER26 : regROUTERADD:= "011010";
constant ROUTER27 : regROUTERADD:= "011011";
constant ROUTER28 : regROUTERADD:= "011100";
constant ROUTER29 : regROUTERADD:= "011101";

constant ROUTER30 : regROUTERADD:= "011110";
constant ROUTER31 : regROUTERADD:= "011111";
constant ROUTER32 : regROUTERADD:= "100000";
constant ROUTER33 : regROUTERADD:= "100001";
constant ROUTER34 : regROUTERADD:= "100010";
constant ROUTER35 : regROUTERADD:= "100011";
constant ROUTER36 : regROUTERADD:= "100100";
constant ROUTER37 : regROUTERADD:= "100101";
constant ROUTER38 : regROUTERADD:= "100110";
constant ROUTER39 : regROUTERADD:= "100111";

constant ROUTER40 : regROUTERADD:= "101000";
constant ROUTER41 : regROUTERADD:= "101001";
constant ROUTER42 : regROUTERADD:= "101010";
constant ROUTER43 : regROUTERADD:= "101011";
constant ROUTER44 : regROUTERADD:= "101100";
constant ROUTER45 : regROUTERADD:= "101101";
constant ROUTER46 : regROUTERADD:= "101110";
constant ROUTER47 : regROUTERADD:= "101111";
constant ROUTER48 : regROUTERADD:= "110000";
constant ROUTER49 : regROUTERADD:= "110001";

constant ROUTER50 : regROUTERADD:= "110010";
constant ROUTER51 : regROUTERADD:= "110011";
constant ROUTER52 : regROUTERADD:= "110100";
constant ROUTER53 : regROUTERADD:= "110101";
constant ROUTER54 : regROUTERADD:= "110110";
constant ROUTER55 : regROUTERADD:= "110111";
constant ROUTER56 : regROUTERADD:= "111000";
constant ROUTER57 : regROUTERADD:= "111001";
constant ROUTER58 : regROUTERADD:= "111010";
constant ROUTER59 : regROUTERADD:= "111011";

constant ROUTER60 : regROUTERADD:= "111100";
constant ROUTER61 : regROUTERADD:= "111101";
constant ROUTER62 : regROUTERADD:= "111110";
constant ROUTER63 : regROUTERADD:= "111111";

constant MASTER0 		: regPORTADD:= "0000";
constant MASTER1 		: regPORTADD:= "0001";
constant MASTER2 		: regPORTADD:= "0010";
constant MASTER3 		: regPORTADD:= "0011";
constant MASTER4 		: regPORTADD:= "0100";
constant MASTER5 		: regPORTADD:= "0101";
constant MASTER6 		: regPORTADD:= "0110";
constant MASTER7 		: regPORTADD:= "0111";
constant MASTER8 		: regPORTADD:= "1000";
constant MASTER9 		: regPORTADD:= "1001";
constant MASTER10	: regPORTADD:= "1010";
constant MASTER11	: regPORTADD:= "1011";
constant MASTER12	: regPORTADD:= "1100";
constant MASTER13	: regPORTADD:= "1101";
constant MASTER14	: regPORTADD:= "1110";
constant MASTER15	: regPORTADD:= "1111";

constant SLAVE0 		: regPORTADD:= "0000";
constant SLAVE1 		: regPORTADD:= "0001";
constant SLAVE2 		: regPORTADD:= "0010";
constant SLAVE3 		: regPORTADD:= "0011";
constant SLAVE4 		: regPORTADD:= "0100";
constant SLAVE5 		: regPORTADD:= "0101";
constant SLAVE6 		: regPORTADD:= "0110";
constant SLAVE7 		: regPORTADD:= "0111";
constant SLAVE8 		: regPORTADD:= "1000";
constant SLAVE9 		: regPORTADD:= "1001";
constant SLAVE10 		: regPORTADD:= "1010";
constant SLAVE11 		: regPORTADD:= "1011";
constant SLAVE12 		: regPORTADD:= "1100";
constant SLAVE13 		: regPORTADD:= "1101";
constant SLAVE14 		: regPORTADD:= "1110";
constant SLAVE15 		: regPORTADD:= "1111";

constant ROUTINGPORT0 	: regPORTADD:= "0000";
constant ROUTINGPORT1 	: regPORTADD:= "0001";
constant ROUTINGPORT2 	: regPORTADD:= "0010";
constant ROUTINGPORT3 	: regPORTADD:= "0011";
constant ROUTINGPORT4 	: regPORTADD:= "0100";
constant ROUTINGPORT5 	: regPORTADD:= "0101";
constant ROUTINGPORT6 	: regPORTADD:= "0110";
constant ROUTINGPORT7 	: regPORTADD:= "0111";
constant ROUTINGPORT8 	: regPORTADD:= "1000";
constant ROUTINGPORT9 	: regPORTADD:= "1001";
constant ROUTINGPORT10 	: regPORTADD:= "1010";
constant ROUTINGPORT11 	: regPORTADD:= "1011";
constant ROUTINGPORT12 	: regPORTADD:= "1100";
constant ROUTINGPORT13 	: regPORTADD:= "1101";
constant ROUTINGPORT14 	: regPORTADD:= "1110";
constant ROUTINGPORT15 	: regPORTADD:= "1111";


----------------------------------------------------------------
				 ----- CONFIGURABLE PART  -----
----------------------------------------------------------------

------ 1) MASTER, SLAVE and ROUTING PORT NUMBERS by ROUTER ------
--for each router, declare the number of master interface port(s), slave interface port(s) and routing port(s)
constant R0_MASTER_SLAVE_ROUTPORT_NB : record_master_routport_slave_nb_by_router :=(4,5,2);
constant R1_MASTER_SLAVE_ROUTPORT_NB : record_master_routport_slave_nb_by_router :=(0,2,4);
constant R2_MASTER_SLAVE_ROUTPORT_NB : record_master_routport_slave_nb_by_router :=(4,1,1);
constant R3_MASTER_SLAVE_ROUTPORT_NB : record_master_routport_slave_nb_by_router :=(3,0,3);
constant R4_MASTER_SLAVE_ROUTPORT_NB : record_master_routport_slave_nb_by_router :=(4,4,3);
constant R5_MASTER_SLAVE_ROUTPORT_NB : record_master_routport_slave_nb_by_router :=(1,1,1);

-- => AGGREGATING ARRAY <= --
--aggregate all the "Ri_MASTER_SLAVE_ROUTPORT_NB" in this array
constant ALL_ROUTER_MASTER_SLAVE_ROUTPORT_NB : array_all_record_master_routport_slave_nb_by_router:=(
	R0_MASTER_SLAVE_ROUTPORT_NB,
	R1_MASTER_SLAVE_ROUTPORT_NB,
	R2_MASTER_SLAVE_ROUTPORT_NB,
	R3_MASTER_SLAVE_ROUTPORT_NB,
	R4_MASTER_SLAVE_ROUTPORT_NB,
	R5_MASTER_SLAVE_ROUTPORT_NB
);


------ 2) MASTER and SLAVE RANKS ------
--a vector composed of all the masters and a vector composed of all the slaves are used to assignate
--the master and slave interface signals to each router. These ranks are used to indicate at which location
--are situated the first master interface and the slave interface of each router in the vectors containing all master
--signals and all slave signals.
--These 2 variables must have a value for each router:
-- a) The first value is always '0'
-- b) If the current router does not have any MASTER/SLAVE the value must be '0' (MASTER for MASTER_RANK and SLAVE for SLAVE_RANK)
-- c) The value for the next router is equal to the current value plus the number of MASTER/SLAVE in the current router (cumulated sum of all the precedent MASTER/SLAVE)
constant MASTER_RANK : master_rank_in_vector := (0,0,4,8,11,15);
constant SLAVE_RANK  : slave_rank_in_vector  := (0,5,7,0,8,12);

------ 3) ROUTER CONNEXIONS (topology)------
--define a record for each connexion between routers
--wgeb two routers are connected : only one ROUTER_CONNEXION constant must be defined
--4 values to define for each connexion:
-- 1) SOURCE_ROUTER					
-- 2) SOURCE_ROUTING_PORT				
-- 3) DESTINATION_ROUTER				
-- 4) DESTINATION_ROUTING_PORT		
constant ROUTER_CONNEXION_0 : record_router_connexion :=(0,9,1,2);
constant ROUTER_CONNEXION_1 : record_router_connexion :=(0,10,3,3);  
constant ROUTER_CONNEXION_2 : record_router_connexion :=(1,4,3,4); 
constant ROUTER_CONNEXION_3 : record_router_connexion :=(1,5,4,10);
constant ROUTER_CONNEXION_4 : record_router_connexion :=(2,5,1,3);
constant ROUTER_CONNEXION_5 : record_router_connexion :=(3,5,4,8); 
constant ROUTER_CONNEXION_6 : record_router_connexion :=(4,9,5,1);

-- => AGGREGATING ARRAY <= --
constant ALL_ROUTER_CONNEXIONS : array_all_router_connexion:=(
	ROUTER_CONNEXION_0,
	ROUTER_CONNEXION_1,
	ROUTER_CONNEXION_2,
	ROUTER_CONNEXION_3,
	ROUTER_CONNEXION_4,
	ROUTER_CONNEXION_5,
	ROUTER_CONNEXION_6
);

------ 4) PACKET INTERFACE DECLARATION ------
--define a Ri_PACKET_INTERFACE_PORT_ADD constant for each router.
--this constants have a value for each port of the router (0 to 15).
--the value tells if the current router port have a packet interface and which type is it.
--There is four different choices for each router port:
-- '0': no packet interface
-- '1': master packet interface
-- '2': slave packet interface
-- '3': routing port interface
--The first value correspond to "PORT0" of the router, second value to "PORT1" of the ROUTER, etc ...
constant R0_PACKET_INTERFACE_PORT_ADD : packet_interface_portadd_vector := (1,1,1,1,2,2,2,2,2,3,3,0,0,0,0,0); 
constant R1_PACKET_INTERFACE_PORT_ADD : packet_interface_portadd_vector := (2,2,3,3,3,3,0,0,0,0,0,0,0,0,0,0);
constant R2_PACKET_INTERFACE_PORT_ADD : packet_interface_portadd_vector := (1,1,1,1,2,3,0,0,0,0,0,0,0,0,0,0); 
constant R3_PACKET_INTERFACE_PORT_ADD : packet_interface_portadd_vector := (1,1,1,3,3,3,0,0,0,0,0,0,0,0,0,0); 
constant R4_PACKET_INTERFACE_PORT_ADD : packet_interface_portadd_vector := (1,1,1,1,2,2,2,2,3,3,3,0,0,0,0,0);
constant R5_PACKET_INTERFACE_PORT_ADD : packet_interface_portadd_vector := (1,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0); 

-- => AGGREGATING ARRAY <= --
constant ALL_ROUTER_PACKET_INTERFACE_PORT_ADD : array_all_router_packet_interface_portadd:=(
	R0_PACKET_INTERFACE_PORT_ADD,
	R1_PACKET_INTERFACE_PORT_ADD,
	R2_PACKET_INTERFACE_PORT_ADD,
	R3_PACKET_INTERFACE_PORT_ADD,
	R4_PACKET_INTERFACE_PORT_ADD,
	R5_PACKET_INTERFACE_PORT_ADD);
	
	
------ 5) ADDRESS DECODER TABLE SIZES  ------
--define the size of each address decoding table of each master of each router (in the number of rules that it contain)
constant ROUTER0_MASTER0_ADD_DECOD_TABLE_SIZE 	: integer := 9;
constant ROUTER0_MASTER1_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER0_MASTER2_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER0_MASTER3_ADD_DECOD_TABLE_SIZE 	: integer := 8;
																				
constant ROUTER2_MASTER0_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER2_MASTER1_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER2_MASTER2_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER2_MASTER3_ADD_DECOD_TABLE_SIZE 	: integer := 8;
																				
constant ROUTER3_MASTER0_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER3_MASTER1_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER3_MASTER2_ADD_DECOD_TABLE_SIZE 	: integer := 8;
																				
constant ROUTER4_MASTER0_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER4_MASTER1_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER4_MASTER2_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER4_MASTER3_ADD_DECOD_TABLE_SIZE 	: integer := 8;
																				
constant ROUTER5_MASTER0_ADD_DECOD_TABLE_SIZE 	: integer := 9;

--define the total number of address decoding rules (for all the masters)
constant TOTAL_ADDRESS_DECOD_SIZE 				: integer := 130;


------ 6) SLAVE ADDRESS MAPPING (32-bits) ------
--This address mapping is used inside the address decoding tables.
--for each master of each router, define the address mapping of slave interfaces that can be reached by the master 
--for each slave -> define a BASE_ADD and a HIGH_ADD
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER0_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER5_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"50000000";
constant	ROUTER0_MASTER0_address_mapping_for_ROUTER5_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"50FFFFFF";

constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"40000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"40FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER0_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"40000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"40FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER0_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER4_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"42000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER4_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"42FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER0_MASTER3_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"000AAA00";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER2_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER2_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER2_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER2_MASTER3_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";


constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER3_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER3_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER3_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";


constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER4_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER4_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER4_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER4_MASTER3_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";


constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"40000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"40FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"41000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"41FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"42000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"42FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"43000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"43FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER5_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"50000000";
constant	ROUTER5_MASTER0_address_mapping_for_ROUTER5_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"50FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant	ROUTER5_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";



---- 7) ROUTING TABLE CONTENTS ------
--define the address port that must take a packet to reach the DESTINATION ROUTER FROM the current ROUTER
--for each router a port address must be defined to reach all the other routers of the network
constant from_ROUTER0_to_ROUTER1_destination_port : regPORTADD:= ROUTINGPORT9;
constant from_ROUTER0_to_ROUTER2_destination_port : regPORTADD:= ROUTINGPORT9;
constant from_ROUTER0_to_ROUTER3_destination_port : regPORTADD:= ROUTINGPORT10;
constant from_ROUTER0_to_ROUTER4_destination_port : regPORTADD:= ROUTINGPORT9;
constant from_ROUTER0_to_ROUTER5_destination_port : regPORTADD:= ROUTINGPORT10;

constant from_ROUTER1_to_ROUTER0_destination_port : regPORTADD:= ROUTINGPORT2;
constant from_ROUTER1_to_ROUTER2_destination_port : regPORTADD:= ROUTINGPORT3;
constant from_ROUTER1_to_ROUTER3_destination_port : regPORTADD:= ROUTINGPORT4;
constant from_ROUTER1_to_ROUTER4_destination_port : regPORTADD:= ROUTINGPORT5;
constant from_ROUTER1_to_ROUTER5_destination_port : regPORTADD:= ROUTINGPORT5;

constant from_ROUTER2_to_ROUTER0_destination_port : regPORTADD:= ROUTINGPORT5;
constant from_ROUTER2_to_ROUTER1_destination_port : regPORTADD:= ROUTINGPORT5;
constant from_ROUTER2_to_ROUTER3_destination_port : regPORTADD:= ROUTINGPORT5;
constant from_ROUTER2_to_ROUTER4_destination_port : regPORTADD:= ROUTINGPORT5;
constant from_ROUTER2_to_ROUTER5_destination_port : regPORTADD:= ROUTINGPORT5;

constant from_ROUTER3_to_ROUTER0_destination_port : regPORTADD:= ROUTINGPORT3;
constant from_ROUTER3_to_ROUTER1_destination_port : regPORTADD:= ROUTINGPORT4;
constant from_ROUTER3_to_ROUTER2_destination_port : regPORTADD:= ROUTINGPORT4;
constant from_ROUTER3_to_ROUTER4_destination_port : regPORTADD:= ROUTINGPORT5;
constant from_ROUTER3_to_ROUTER5_destination_port : regPORTADD:= ROUTINGPORT5;

constant from_ROUTER4_to_ROUTER0_destination_port : regPORTADD:= ROUTINGPORT8;
constant from_ROUTER4_to_ROUTER1_destination_port : regPORTADD:= ROUTINGPORT10;
constant from_ROUTER4_to_ROUTER2_destination_port : regPORTADD:= ROUTINGPORT10;
constant from_ROUTER4_to_ROUTER3_destination_port : regPORTADD:= ROUTINGPORT8;
constant from_ROUTER4_to_ROUTER5_destination_port : regPORTADD:= ROUTINGPORT9;

constant from_ROUTER5_to_ROUTER0_destination_port : regPORTADD:= ROUTINGPORT2;
constant from_ROUTER5_to_ROUTER1_destination_port : regPORTADD:= ROUTINGPORT2;
constant from_ROUTER5_to_ROUTER2_destination_port : regPORTADD:= ROUTINGPORT2;
constant from_ROUTER5_to_ROUTER3_destination_port : regPORTADD:= ROUTINGPORT2;
constant from_ROUTER5_to_ROUTER4_destination_port : regPORTADD:= ROUTINGPORT2;



------ 8) ADDRESS DECODER TYPES ------
--define the size of each address decoding table of each master of each router (in the number of rules that it contain)
type router0_master0_record_address_decod_table is array (0 to ROUTER0_MASTER0_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router0_master1_record_address_decod_table is array (0 to ROUTER0_MASTER1_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router0_master2_record_address_decod_table is array (0 to ROUTER0_MASTER2_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router0_master3_record_address_decod_table is array (0 to ROUTER0_MASTER3_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
                                                                                                   
type router2_master0_record_address_decod_table is array (0 to ROUTER2_MASTER0_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router2_master1_record_address_decod_table is array (0 to ROUTER2_MASTER1_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router2_master2_record_address_decod_table is array (0 to ROUTER2_MASTER2_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router2_master3_record_address_decod_table is array (0 to ROUTER2_MASTER3_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
                                                                                                   
type router3_master0_record_address_decod_table is array (0 to ROUTER3_MASTER0_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router3_master1_record_address_decod_table is array (0 to ROUTER3_MASTER1_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router3_master2_record_address_decod_table is array (0 to ROUTER3_MASTER2_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
                                                                                                   
type router4_master0_record_address_decod_table is array (0 to ROUTER4_MASTER0_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router4_master1_record_address_decod_table is array (0 to ROUTER4_MASTER1_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router4_master2_record_address_decod_table is array (0 to ROUTER4_MASTER2_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router4_master3_record_address_decod_table is array (0 to ROUTER4_MASTER3_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
                                                                                                    
type router5_master0_record_address_decod_table is array (0 to ROUTER5_MASTER0_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;

type unconstrained_array_record_address_decod_table is array (natural range <>) of record_master_interface_address_decode_routing_table;


------ 9) ADDRESS DECODER TABLES ------

-- constant ROUTERi_MASTERj_ADDRESS_DECODER_TABLE : router0_master0_record_address_decod_table:=(
-- |    destination slave   |   destination slave 	    |   		   Routing table 				  | slave destination |   
-- |	   base address	    | 	   high address         |	 	    local port noc address		  	  |      address      |
constant ROUTER0_MASTER0_ADDRESS_DECODER_TABLE : router0_master0_record_address_decod_table:=(
	(ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, SLAVE4, ROUTER0 & SLAVE4),	
	(ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, SLAVE5, ROUTER0 & SLAVE5),	
	(ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, SLAVE6, ROUTER0 & SLAVE6),	
	(ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, SLAVE7, ROUTER0 & SLAVE7),	
	(ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, SLAVE8, ROUTER0 & SLAVE8),	
	(ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER0_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER0_to_ROUTER2_destination_port, ROUTER2 & SLAVE4),
	(ROUTER0_MASTER0_address_mapping_for_ROUTER5_SLAVE1_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER5_SLAVE1_HIGH_ADD, from_ROUTER0_to_ROUTER5_destination_port, ROUTER5 & SLAVE1)
	);
	
constant ROUTER0_MASTER1_ADDRESS_DECODER_TABLE : router0_master1_record_address_decod_table:=(
	(ROUTER0_MASTER1_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD, from_ROUTER0_to_ROUTER4_destination_port, ROUTER4 & SLAVE4),	
	(ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, SLAVE5, ROUTER0 & SLAVE5),	
	(ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, SLAVE6, ROUTER0 & SLAVE6),	
	(ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, SLAVE7, ROUTER0 & SLAVE7),	
	(ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, SLAVE8, ROUTER0 & SLAVE8),	
	(ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER0_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER0_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);

constant ROUTER0_MASTER2_ADDRESS_DECODER_TABLE : router0_master2_record_address_decod_table:=(
	(ROUTER0_MASTER2_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD, from_ROUTER0_to_ROUTER4_destination_port, ROUTER4 & SLAVE4),	
	(ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, SLAVE5, ROUTER0 & SLAVE5),	
	(ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, SLAVE6, ROUTER0 & SLAVE6),	
	(ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, SLAVE7, ROUTER0 & SLAVE7),	
	(ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, SLAVE8, ROUTER0 & SLAVE8),	
	(ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER0_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER0_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);
	
constant ROUTER0_MASTER3_ADDRESS_DECODER_TABLE : router0_master3_record_address_decod_table:=(
	(ROUTER0_MASTER3_address_mapping_for_ROUTER4_SLAVE6_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER4_SLAVE6_HIGH_ADD, from_ROUTER0_to_ROUTER4_destination_port, ROUTER4 & SLAVE4),	
	(ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, SLAVE5, ROUTER0 & SLAVE5),	
	(ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, SLAVE6, ROUTER0 & SLAVE6),	
	(ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, SLAVE7, ROUTER0 & SLAVE7),	
	(ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, SLAVE8, ROUTER0 & SLAVE8),	
	(ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER0_MASTER3_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER0_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);

constant ROUTER2_MASTER0_ADDRESS_DECODER_TABLE : router2_master0_record_address_decod_table:=(
	(ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD, from_ROUTER2_to_ROUTER4_destination_port, ROUTER4 & SLAVE4),	
	(ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE5_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE5_HIGH_ADD, from_ROUTER2_to_ROUTER4_destination_port, ROUTER4 & SLAVE5),	
	(ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE6_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE6_HIGH_ADD, from_ROUTER2_to_ROUTER4_destination_port, ROUTER4 & SLAVE6),	
	(ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE7_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE7_HIGH_ADD, from_ROUTER2_to_ROUTER4_destination_port, ROUTER4 & SLAVE7),	
	(ROUTER2_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER2_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, SLAVE4, ROUTER2 & SLAVE4)
	);
	
constant ROUTER2_MASTER1_ADDRESS_DECODER_TABLE : router2_master1_record_address_decod_table:=(
	(ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER2_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, SLAVE4, ROUTER2 & SLAVE4)
	);

constant ROUTER2_MASTER2_ADDRESS_DECODER_TABLE : router2_master2_record_address_decod_table:=(
	(ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER2_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, SLAVE4, ROUTER2 & SLAVE4)
	);
	
constant ROUTER2_MASTER3_ADDRESS_DECODER_TABLE : router2_master3_record_address_decod_table:=(
	(ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER2_MASTER3_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, SLAVE4, ROUTER2 & SLAVE4)
	);
	
constant ROUTER3_MASTER0_ADDRESS_DECODER_TABLE : router3_master0_record_address_decod_table:=(
	(ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER3_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER3_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER3_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER3_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);
	
constant ROUTER3_MASTER1_ADDRESS_DECODER_TABLE : router3_master1_record_address_decod_table:=(
	(ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER3_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER3_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER3_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER3_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);

constant ROUTER3_MASTER2_ADDRESS_DECODER_TABLE : router3_master2_record_address_decod_table:=(
	(ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER3_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER3_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER3_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER3_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);
	
	
constant ROUTER4_MASTER0_ADDRESS_DECODER_TABLE : router4_master0_record_address_decod_table:=(
	(ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER4_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);
	
constant ROUTER4_MASTER1_ADDRESS_DECODER_TABLE : router4_master1_record_address_decod_table:=(
	(ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER4_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);

constant ROUTER4_MASTER2_ADDRESS_DECODER_TABLE : router4_master2_record_address_decod_table:=(
	(ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER4_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);
	
constant ROUTER4_MASTER3_ADDRESS_DECODER_TABLE : router4_master3_record_address_decod_table:=(
	(ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER4_MASTER3_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);
	
constant ROUTER5_MASTER0_ADDRESS_DECODER_TABLE : router5_master0_record_address_decod_table:=(
	(ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER5_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER5_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),	
	(ROUTER5_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER5_to_ROUTER2_destination_port, ROUTER2 & SLAVE4),	
	(ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD, from_ROUTER5_to_ROUTER4_destination_port, ROUTER4 & SLAVE4),	
	(ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE5_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE5_HIGH_ADD, from_ROUTER5_to_ROUTER4_destination_port, ROUTER4 & SLAVE5),	
	(ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE6_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE6_HIGH_ADD, from_ROUTER5_to_ROUTER4_destination_port, ROUTER4 & SLAVE6),
	(ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE7_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE7_HIGH_ADD, from_ROUTER5_to_ROUTER4_destination_port, ROUTER4 & SLAVE7),
	(ROUTER5_MASTER0_address_mapping_for_ROUTER5_SLAVE1_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER5_SLAVE1_HIGH_ADD, SLAVE4, ROUTER5 & SLAVE4),
	(ROUTER5_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER5_to_ROUTER0_destination_port, ROUTER0 & SLAVE4)
	);
	
	
-- => AGGREGATING ARRAY <= --
--aggregates all master address decoder rules : starting from ROUTER0 - MASTER0 - RULES0 => first increment RULE number, then increment MASTER number, and finally increment ROUTER number
--concantenate all the rules with a "&"
constant ALL_MASTER_ADDRESS_DECODER_TABLES : unconstrained_array_record_address_decod_table:=(
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(0) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(1) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(2) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(3) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(4) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(5) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(6) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(7) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(8) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(0) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(1) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(2) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(3) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(4) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(5) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(6) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(7) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(0) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(1) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(2) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(3) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(4) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(5) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(6) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(7) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(0) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(1) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(2) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(3) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(4) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(5) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(6) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(7) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(0) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(1) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(2) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(3) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(4) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(5) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(6) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(7) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(0) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(1) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(2) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(3) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(4) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(5) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(6) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(7) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(0) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(1) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(2) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(3) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(4) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(5) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(6) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(7) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(0) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(1) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(2) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(3) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(4) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(5) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(6) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(7) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(0) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(1) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(2) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(3) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(4) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(5) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(6) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(7) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(0) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(1) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(2) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(3) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(4) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(5) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(6) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(7) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(0) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(1) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(2) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(3) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(4) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(5) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(6) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(7) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(0) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(1) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(2) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(3) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(4) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(5) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(6) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(7) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(0) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(1) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(2) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(3) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(4) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(5) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(6) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(7) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(0) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(1) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(2) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(3) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(4) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(5) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(6) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(7) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(0) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(1) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(2) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(3) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(4) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(5) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(6) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(7) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(0) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(1) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(2) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(3) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(4) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(5) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(6) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(7) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(8)
	);
	
	
------ 10) ADDRESS DECODER PARAMETER MATRIX ------
--one line for each router (from 0 to y)
--one column for each master of each router (from 0 to 14)
--the goal is to define one couple of value "(MASTER_TABLE_RANK_NB, MASTER_DECOD_TABLE_SIZE)" for each master of each router
--MASTER_TABLE_RANK_NB = rank of the address decoding rule in the total number of rules (it is equal to the cumulated number of rules in the previous master address decoders)
--MASTER_DECOD_TABLE_SIZE = number of address decoding rule in the current master address decoder table
constant ADD_DECODER_PARAMETER_MX :  matrix_add_decoder_parameter :=(
((0,9), 	(9,8), 		(17,8), 	(25,8), 	(0,0), 		(0,0), 		(0,0), 		(0,0), 	(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0)), 	-- ROUTER 0
((0,0), 	(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 	(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0)),	-- ROUTER 1
((33,8), 	(41,8),		(49,8), 	(57,8), 	(0,0), 		(0,0), 		(0,0), 		(0,0), 	(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0)),	-- ROUTER 2
((65,8), 	(73,8),	 	(81,8), 	(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 	(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0)),	-- ROUTER 3
((89,8), 	(97,8),	 	(105,8), 	(113,8), 	(0,0), 		(0,0), 		(0,0), 		(0,0), 	(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0)),	-- ROUTER 4
((121,9), 	(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 	(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0))    -- ROUTER 5
);
--MASTER	MASTER		MASTER		MASTER		MASTER		MASTER		MASTER		MASTER	MASTER...
--0			1			2			3			4			5			6			7		8		9	   10	  11    12     13      14   
	
	

------ 11) ROUTING TABLE  -------
--define for each router a routing table that gives the destination port to take
--to reach all the other routers of the network.
-- 1rst value) router destination address in regROUTERADD format.
-- 2nd value) local router port address
constant ROUTER0_ROUTING_TABLE : routing_table_array:=(
	(ROUTER1, from_ROUTER0_to_ROUTER1_destination_port),
	(ROUTER2, from_ROUTER0_to_ROUTER2_destination_port),
	(ROUTER3, from_ROUTER0_to_ROUTER3_destination_port),
	(ROUTER4, from_ROUTER0_to_ROUTER4_destination_port),
	(ROUTER5, from_ROUTER0_to_ROUTER5_destination_port));
		
constant ROUTER1_ROUTING_TABLE : routing_table_array:=( 
	(ROUTER0, from_ROUTER1_to_ROUTER0_destination_port),
	(ROUTER2, from_ROUTER1_to_ROUTER2_destination_port),
	(ROUTER3, from_ROUTER1_to_ROUTER3_destination_port),
	(ROUTER4, from_ROUTER1_to_ROUTER4_destination_port),
	(ROUTER5, from_ROUTER1_to_ROUTER5_destination_port));
		
constant ROUTER2_ROUTING_TABLE : routing_table_array:=(
	(ROUTER0, from_ROUTER2_to_ROUTER0_destination_port),
	(ROUTER1, from_ROUTER2_to_ROUTER1_destination_port),
	(ROUTER3, from_ROUTER2_to_ROUTER3_destination_port),
	(ROUTER4, from_ROUTER2_to_ROUTER4_destination_port),
	(ROUTER5, from_ROUTER2_to_ROUTER5_destination_port));
	
constant ROUTER3_ROUTING_TABLE : routing_table_array:=(
	(ROUTER0, from_ROUTER3_to_ROUTER0_destination_port),
	(ROUTER1, from_ROUTER3_to_ROUTER1_destination_port),
	(ROUTER2, from_ROUTER3_to_ROUTER2_destination_port),
	(ROUTER4, from_ROUTER3_to_ROUTER4_destination_port),
	(ROUTER5, from_ROUTER3_to_ROUTER5_destination_port));
		
constant ROUTER4_ROUTING_TABLE : routing_table_array:=( 
	(ROUTER0, from_ROUTER4_to_ROUTER0_destination_port),
	(ROUTER1, from_ROUTER4_to_ROUTER1_destination_port),
	(ROUTER2, from_ROUTER4_to_ROUTER2_destination_port),
	(ROUTER3, from_ROUTER4_to_ROUTER3_destination_port),
	(ROUTER5, from_ROUTER4_to_ROUTER5_destination_port));
		
constant ROUTER5_ROUTING_TABLE : routing_table_array:=( 
	(ROUTER0, from_ROUTER5_to_ROUTER0_destination_port),
	(ROUTER1, from_ROUTER5_to_ROUTER1_destination_port),
	(ROUTER2, from_ROUTER5_to_ROUTER2_destination_port),
	(ROUTER3, from_ROUTER5_to_ROUTER3_destination_port),
	(ROUTER4, from_ROUTER5_to_ROUTER4_destination_port));
	
-- => AGGREGATING ARRAY <= --
constant ALL_ROUTING_TABLES : array_all_routing_tables:=(
	ROUTER0_ROUTING_TABLE,
	ROUTER1_ROUTING_TABLE,
	ROUTER2_ROUTING_TABLE,
	ROUTER3_ROUTING_TABLE,
	ROUTER4_ROUTING_TABLE,
	ROUTER5_ROUTING_TABLE
);


------ 12) LOCAL CONNEXIONS MATRIX -------
--defining for each router local connexions between master and slave interface
--'0': no connexion
--'1': router local connexion between MASTERi and SLAVEj
--if a slave is connected to only one master -> initialize single master to '1' and give the number of the correspondant master
--if a master is connected to only one slave -> initialize single slave to '1' and give the number of the correspondant slave  
constant ROUTER0_LOCAL_MX    : local_connexion_matrix :=( 		  
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 0
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 1
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 2
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 3
	  (1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 4
	  (1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 5
	  (1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 6
	  (1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 7
	  (1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 8
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 9
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 10
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 11
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 12
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 13
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 14
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- single_slave
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0));-- slave_rank
	-- m m m m m m m m m m m m m m m s m
	-- a a a a a a a a a a a a a a a i a
	-- s s s s s s s s s s s s s s s n s
	-- t t t t t t t t t t t t t t t g t
	-- e e e e e e e e e e e e e e e l e
	-- r r r r r r r r r r r r r r r e r
	-- 0 1 2 3 4 5 6 7 8 9 1 1 1 1 1 _ _
	--                     0 1 2 3 4 m r
	--								 a a								
	--								 s n
	--								 t k
	--								 e 
	--								 r 
	--                                 
	
constant ROUTER1_LOCAL_MX    : local_connexion_matrix :=( 		  
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 0
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 1
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 2
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 3
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 4
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 5
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 6
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 7
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 8
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 9
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 10
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 11
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 12
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 13
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 14
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- single_slave
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0));-- slave rank 
	-- m m m m m m m m m m m m m m m s m
	-- 0 1 2 3 4 5 6 7 8 9 1 1 1 1 1 m r
	--					     0 1 2 3 4 
	
	
constant ROUTER2_LOCAL_MX    : local_connexion_matrix :=( 		  
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 0
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 1
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 2
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 3
	  (1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 4
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 5
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 6
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 7
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 8
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 9
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 10
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 11
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 12
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 13
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 14
	  (1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0), -- single_slave
	  (4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0));-- slave rank 
	-- m m m m m m m m m m m m m m m s m
	-- 0 1 2 3 4 5 6 7 8 9 1 1 1 1 1 m r
	--					   0 1 2 3 4 
	
constant ROUTER3_LOCAL_MX    : local_connexion_matrix :=( 		  
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 0
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 1
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 2
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 3
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 4
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 5
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 6
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 7
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 8
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 9
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 10
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 11
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 12
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 13
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 14
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- single_slave
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0));-- slave rank 
	-- m m m m m m m m m m m m m m m s m
	-- 0 1 2 3 4 5 6 7 8 9 1 1 1 1 1 m r
	--					   0 1 2 3 4 
	
	
constant ROUTER4_LOCAL_MX    : local_connexion_matrix :=( 		  
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 0
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 1
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 2
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 3
	  (1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 4
	  (1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 5
	  (1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 6
	  (1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 7
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 8
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 9
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 10
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 11
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 12
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 13
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 14
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- single_slave
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0));-- slave rank 
	-- m m m m m m m m m m m m m m m s m
	-- 0 1 2 3 4 5 6 7 8 9 1 1 1 1 1 m r
	-- 					   0 1 2 3 4 
	
	
constant ROUTER5_LOCAL_MX    : local_connexion_matrix :=( 		  
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 0
	  (1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0), -- slave 1
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 2
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 3
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 4
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 5
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 6
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 7
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 8
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 9
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 10
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 11
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 12
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 13
	  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 14
	  (1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- single_slave
	  (1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0));-- slave rank 
	-- m m m m m m m m m m m m m m m s m
	-- 0 1 2 3 4 5 6 7 8 9 1 1 1 1 1 m r
	--					   0 1 2 3 4 
	
-- => AGGREGATING ARRAY <= --
constant ALL_ROUTER_LOCAL_MATRIX : array_all_local_connexion_matrix:=(
	ROUTER0_LOCAL_MX,
	ROUTER1_LOCAL_MX,
	ROUTER2_LOCAL_MX,
	ROUTER3_LOCAL_MX,
	ROUTER4_LOCAL_MX,
	ROUTER5_LOCAL_MX
);
	
	---- FUNCTION DECLARATION ----
	
	function or_reduce(V: std_logic_vector) return std_logic;

end noc_config;


package body noc_config is

	---- FUNCTION DEFINTION ----
	
	--function that apply a logic OR to all the bits of a std_logic_vector
	function or_reduce(V: std_logic_vector)
		return std_logic is
		variable result: std_logic;
	begin
		for i in V'range loop
			if i = V'left then
				result := V(i);
			else
				result := result OR V(i);
			end if;
			exit when result ='1';
		end loop;
		return result;
	end or_reduce;

end noc_config;
