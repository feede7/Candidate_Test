------------------------------------------------------------------------------
-- Company: Satellogic S.A
--
-- File: spi.vhdl
-- Description: SPI Core
--
-- AXI-SPI device for new candidates
--
-- Author: Federico De La Cruz Arbizu
--
--------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity En_SPI is
    generic (
    	C_AXI_DATA_WIDTH 	: integer := 32;
    	C_AXI_ADDR_WIDTH 	: integer := 4;
    	FREQ_AXI_CLK 		: integer := 100_000_000;
    	FREQ_SCLK			: integer :=   1_000_000
	);
    Port ( 
    	CSn 		: out std_logic;
		MOSI 		: out std_logic;
		MISO 		: in  std_logic;
		SCK 		: out std_logic;
		INT 		: out std_logic;
		WDATA     	: in  std_logic_vector(C_AXI_DATA_WIDTH - 1 downto 0);
		RDATA  		: out std_logic_vector(C_AXI_DATA_WIDTH - 1 downto 0);
		RADDR  		: in  std_logic_vector(C_AXI_ADDR_WIDTH - 1 downto 0);
		RENA   		: in  std_logic;
		WENA   		: in  std_logic;
		WADDR  		: in  std_logic_vector(C_AXI_ADDR_WIDTH - 1 downto 0);
		AXI_CLK 	: in  std_logic;
		AXI_RESETn 	: in  std_logic
	);
end En_SPI;

architecture Arq_SPI of En_SPI is
	constant ADDR_TX 	: std_logic_vector(C_AXI_ADDR_WIDTH -1 downto 0) := x"0";
	constant ADDR_RX 	: std_logic_vector(C_AXI_ADDR_WIDTH -1 downto 0) := x"4";

    signal sSCLK		: std_logic;
    signal sCSn			: std_logic;
	signal Div_SCLK 	: integer;
	
	signal WDATA_Buff	: std_logic_vector(C_AXI_DATA_WIDTH-1 downto 0);
	signal RDATA_Buff	: std_logic_vector(C_AXI_DATA_WIDTH-1 downto 0);
	
	type   States_Sender is  (Wait_WENA,Wait_Rising,Wait_Falling);
	signal State_Sender 	: States_Sender := Wait_WENA;
	signal count_sender 	: integer;

begin

    ---------------------------------------------------------
	-- Genero señales necesarias para el SPI desde las señales AXI
	    
	-- AXI_CLK = 100MHz
	-- SCLK = 1MHz
	
	process(AXI_RESETn,AXI_CLK)
	begin
		if AXI_RESETn = '0' or count_sender = 8 then
			Div_SCLK 	<= 1;
			sSCLK		<= '0';
			CSn			<= '1';
		elsif rising_edge(AXI_CLK) then
			CSn	<= '0';
			if Div_SCLK = FREQ_AXI_CLK/FREQ_SCLK/2 then
				sSCLK <= not sSCLK;
				Div_SCLK <= 1;
			else
				Div_SCLK <= Div_SCLK + 1;
			end if;
		end if;
	end process;
	
--     +-------+                                               +---------+
-- CS          |                                               |
--             +-----------------------------------------------+
-- 
--                +--+  +--+  +--+  +--+  +--+  +--+  +--+  +--+
-- CLK            |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
--     +----------+  +--+  +--+  +--+  +--+  +--+  +--+  +--+  +---------+
-- 
--             +-----+-----+-----+-----+-----+-----+-----+-----+
-- OSI +-------+ MSB |     |     |     |     |     |     | LSB +---------+
--             +-----+-----+-----+-----+-----+-----+-----+-----+
-- 
--             +-----+-----+-----+-----+-----+-----+-----+-----+
-- ISO +-------+ MSB |     |     |     |     |     |     | LSB +---------+
--             +-----+-----+-----+-----+-----+-----+-----+-----+
-- 
--                                                              +--+
-- INT                                                          |  |
--     +--------------------------------------------------------+  +-----+

	SPI_Sender:
	process(AXI_RESETn,AXI_CLK)
	begin
		if AXI_RESETn = '0' then
			WDATA_Buff		<= (others => '0');
			RDATA_Buff		<= (others=>'0');
			RDATA			<= (others => '0');
			MOSI			<= '0';
			State_Sender 	<= Wait_WENA;
			count_sender	<= 8;
			INT				<= '0';
		elsif rising_edge(AXI_CLK) then
			SCK <= sSCLK;
			INT	<= '0';

			if RENA = '1' then
				if RADDR = ADDR_RX then
					RDATA	<= RDATA_Buff;
				elsif RADDR = ADDR_TX then
					RDATA	<= WDATA_Buff;
				end if;
			end if;
			
			case State_Sender is
				when Wait_WENA =>
					if WENA = '1' and WADDR = ADDR_TX then
						WDATA_Buff 		<= WDATA;
						RDATA_Buff		<= (others=>'0');
						MOSI			<= WDATA(count_sender-1);
						count_sender	<= count_sender - 1;
						State_Sender	<= Wait_Rising;
					end if;
					
				when Wait_Rising =>
					if sSCLK = '1' then
						RDATA_Buff 		<= RDATA_Buff(RDATA_Buff'high-1 downto 0) & MISO;
						State_Sender 	<= Wait_Falling;
					end if;
									
				when Wait_Falling =>
					if sSCLK = '0' then
						if count_sender > 0 then
							MOSI			<= WDATA(count_sender-1);
							count_sender	<= count_sender-1;
							State_Sender 	<= Wait_Rising;
						else
							count_sender	<= 8;
							INT				<= '1';
							State_Sender 	<= Wait_WENA;
						end if;
					end if;
				
				when others =>
					State_Sender 	<= Wait_WENA;
			
			end case;
		end if;
	end process;
	
end Arq_SPI;
