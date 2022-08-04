MEMORY {
	BRAM : ORIGIN = 0x00000000, LENGTH = 0x0001FC00
}

SECTIONS {
	.memory : {
		. = 0x000000;
		_init*(.text);
		trap_vector*(.text);
		*(.text);
		*(*);
		end = .;
	} > BRAM
}
